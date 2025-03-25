from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone

from .models import Thing, History


@receiver(post_save, sender=Thing)
def create_or_update_history_entry(sender, instance, created, **kwargs):
    previous_history_entry = History.objects.filter(thing=instance).order_by('-validFrom').first()

    if created:
        # If the Thing object has just been created
        thing_location = instance.location

        if thing_location:
            # If a location for the Thing object exists
            history_entry = History.objects.create(
                thing=instance,
                location=thing_location,
                validFrom=timezone.now(),
                validTo=None,
                description=f"{instance.name}, {instance.owner}, {thing_location.name}, {thing_location.city}, "
                            f"{thing_location.street}"
            )
            history_entry.save()
    else:
        if not created:
            if previous_history_entry:
                # Update the validTo field of the previous history entry to the current time
                previous_history_entry.validTo = timezone.now()
                previous_history_entry.save()
        print(instance.location if len(str(instance.location)) > 6 else previous_history_entry.location,)
            # Create a new history entry for the current state of the Thing object.
        history_entry = History.objects.create(
            thing=instance,
            location=instance.location if instance.location.name != "Unknown" else previous_history_entry.location,  # Assign the localization from Thing to History
            validFrom=timezone.now(),
            validTo=None,
            description=f"{instance.name}, {instance.owner}, {instance.location}"
        )
        history_entry.save()


post_save.connect(create_or_update_history_entry, sender=Thing)
