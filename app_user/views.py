from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout


from .forms import RegisterUserForm, LoginForm

# Create your views here.


def register_user(request):

    form = RegisterUserForm

    if request.method == "POST":
        form = RegisterUserForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            login(request, user)
            return redirect("app_thing:all_things")

    context = {
        'form': form
    }

    return render(request, 'register.html', context)


def login_user(request):
    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)

        if form.is_valid():

            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                return redirect('app_thing:all_things')

    context = {
        'form': form
    }

    return render(request, 'login.html', context)


# @login_required(login_url='app_user:login')
def user_logout(request):
    logout(request)

    return redirect('app_thing:all_things')
