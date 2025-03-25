import folium

from geopy.geocoders import Nominatim

from app.settings import HOST
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import DetailView, DeleteView
from django.contrib import messages
from django.http import JsonResponse

from .models import Thing, History, Location, Image
from .forms import ThingForm, ImageForm
from .utils import search_thing


class ThingDetailView(LoginRequiredMixin, DetailView):
    model = Thing

    def get_queryset(self):
        user = self.request.user
        return Thing.objects.filter(owner=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        things = self.get_queryset()
        times = History.objects.filter(thing__in=things)
        context['times'] = times
        return context


class ImageDeleteView(LoginRequiredMixin, DeleteView):
    model = Image

    def get_success_url(self):
        image_id = self.kwargs['pk']
        image = Image.objects.get(id=image_id)
        thing_id = image.thing.id
        return reverse_lazy('app_thing:thing_detail', kwargs={'pk': thing_id})


class LocationDeleteView(LoginRequiredMixin, DeleteView):
    model = Location
    success_url = reverse_lazy("app_thing:locations")


class ThingDeleteView(LoginRequiredMixin, DeleteView):
    model = Thing
    success_url = reverse_lazy("app_thing:all_things")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        images = self.object.image_set.all()

        for image in images:
            image.delete()
        self.object.delete()
        return redirect(self.get_success_url())


@login_required(login_url="app_user:login")
def image_recognition(request, pk: int):
    """
    Render the image recognition page for a specific thing.

    Args:
        request: The HTTP request object.
        pk (int): The primary key of the thing.

    Returns:
        HttpResponse: The rendered image recognition page.
    """
    request.session["user"] = str(request.user.uuid)
    thing = Thing.objects.get(id=pk)

    context = {'thing': thing}

    return render(request, "image_recognition.html", context)


@login_required(login_url="app_user:login")
def scanner(request):
    """
    Render the scanner page.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered scanner page.
    """
    return render(request, "scanner.html")


@login_required(login_url="app_user:login")
def add_image(request, pk: int):
    """
    Render the add image page for a specific thing.

    Args:
        request: The HTTP request object.
        pk (int): The primary key of the thing.

    Returns:
        HttpResponse: The rendered add image page.
    """
    thing = Thing.objects.get(id=pk)

    context = {
        'thing': thing,
    }
    return render(request, 'add_image.html', context)


@login_required(login_url="app_user:login")
def add_thing(request):
    """
    Handle the addition of a new thing.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered add thing page or a redirect to all things page.
    """
    user = request.user

    form = ThingForm(user)
    image_form = ImageForm()
    if request.method == "POST":
        form = ThingForm(user, request.POST)
        files = request.FILES.getlist("image")

        if form.is_valid():
            existing_location = form.cleaned_data['existing_location']
            thing = form.save(commit=False)

            if existing_location:
                location = existing_location
            else:
                city = form.cleaned_data['city']
                street = form.cleaned_data['street']
                street_address = form.cleaned_data['street_address']
                location_name = f"{city}, {street}, {street_address}"
                if len(location_name) > 5:

                    location, created = Location.objects.get_or_create(name=location_name, city=city, street=street,
                                                                       street_address=street_address, owner=user)
                else:
                    location, created = Location.objects.get_or_create(name="Unknown", city="", street="",
                                                                       street_address="", owner=user)
            thing.location = location
            thing.save()

            for i in files:
                Image.objects.create(thing=thing, image=i)
            messages.success(request, "New thing added")
            return redirect('app_thing:all_things')

    context = {
        'form': form,
        'image_form': image_form,
    }

    return render(request, 'app_thing/add_thing.html', context)


@login_required(login_url="app_user:login")
def update_thing(request, pk: int):
    """
    Handle the update of an existing thing.

    Args:
        request: The HTTP request object.
        pk (int): The primary key of the thing.

    Returns:
        HttpResponse: The rendered update thing page or a redirect to all things page.
    """
    thing = Thing.objects.get(id=pk)
    user = request.user
    image_form = ImageForm()
    form = ThingForm(user, instance=thing)

    if request.method == 'POST':
        form = ThingForm(user, request.POST, request.FILES, instance=thing)

        files = request.FILES.getlist("image")

        if form.is_valid():

            existing_location = form.cleaned_data.get('existing_location')
            if existing_location and isinstance(existing_location, Location):
                location = existing_location
            else:
                city = form.cleaned_data['city']
                street = form.cleaned_data['street']
                street_address = form.cleaned_data['street_address']
                location_name = f"{city}, {street}, {street_address}"
                if len(location_name) > 5:
                    location, created = Location.objects.get_or_create(name=location_name, city=city, street=street,
                                                                       street_address=street_address, owner=user)
                else:
                    location = thing.location
            thing = form.save(commit=False)
            thing.location = location
            thing.owner = user
            thing.save()

            for i in files:
                Image.objects.create(thing=thing, image=i)

        return redirect('app_thing:all_things')

    context = {'form': form, 'thing': thing, 'image_form': image_form}
    return render(request, 'app_thing/thing_update.html', context)


@login_required(login_url="app_user:login")
def things_map(request):
    """
    Render the map with all things for the logged-in user.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered map page.
    """
    user = request.user
    things = Thing.objects.filter(owner=user)

    locations = Location.objects.filter(location__owner=user).distinct()

    m = folium.Map(location=[52.23744465, 21.00517975187278], zoom_start=8)
    geolocator = Nominatim(user_agent="FindMe")
    for place, thing in zip(locations, things):
        things_at_location = Thing.objects.filter(location=place)
        popup_html = f"<h3>{place.city} {place.street}</h3>"
        popup_html += "<p>"
        for f in things_at_location:
            des = f.description
            popup_html += f"<p>{des}</p></br><a href='{HOST}/thing/{f.id}/' target='_blank'>{str(f)}</a>"
        popup_html += "</p>"

        try:
            location = geolocator.geocode(f"{place.name}")
            if location:
                longitude = location.longitude
                latitude = location.latitude
                coordinates = (latitude, longitude)
                iframe = folium.IFrame(popup_html, width=200, height=200)
                popup = folium.Popup(iframe, max_width=400)
                folium.Marker(coordinates, popup=popup).add_to(m)

        except Exception as e:
            print(f"Error: {e}")

    context = {'map': m._repr_html_()}
    return render(request, 'app_thing/things_map.html', context)


@login_required(login_url="app_user:login")
def all_user_things(request):
    """
    Render the page with all things for the logged-in user.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered all things page or a JSON response with search results.
    """
    user = request.user
    things = Thing.objects.filter(owner=user)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        query = request.GET.get('query', '')
        if query:
            if len(query) >= 3:
                things, search_query = search_thing(query, things)

        results = [
                {
                    'id': thing.id,
                    'name': thing.name,
                    'owner': thing.owner.username,
                    'location': thing.location.name if thing.location else "",
                    'image': thing.image_set.first().image.url if thing.image_set.exists() else None
                }
                for thing in things
            ]

        return JsonResponse(results, safe=False)

    times = History.objects.filter(thing__in=things)

    context = {
        'things': things,
        'times': times,
    }

    return render(request, 'all_things.html', context)

@login_required(login_url="app_user:login")
def location_management(request):
    """
    Render the location management page for the logged-in user.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered location management page.
    """
    locations = Location.objects.filter(owner=request.user)
    context = {
        'locations': locations
    }
    return render(request, 'app_thing/locations.html', context)

@login_required(login_url="app_user:login")
def about(request):
    """
    Render the about page.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered about page.
    """
    return render(request, 'about.html')
