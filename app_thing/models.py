from django.db import models
# from django.utils.translation import gettext_lazy as _
from app_user.models import CustomUser
from .middleware import thread

import uuid


class Location(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    street_address = models.CharField(max_length=10)

    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name_plural = 'Location'
        ordering = ['id']


class Thing(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    description = models.TextField()
    barcode = models.BigIntegerField(blank=True, null=True)

    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='location')

    class Meta:
        verbose_name_plural = 'Things'
        ordering = ['id']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk is None and self.owner is None:
            self.owner = thread.user
        return super(Thing, self).save(*args, **kwargs)

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''

        return url


class History(models.Model):
    thing = models.ForeignKey(Thing, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    validFrom = models.DateTimeField(auto_now_add=True)
    validTo = models.DateTimeField(auto_now=False, null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return f"Name: {self.thing.name}, owner: {self.thing.owner}, location: {self.location}"

    class Meta:
        verbose_name_plural = 'History'
        ordering = ['id']


class ImageTag(models.Model):
    name = models.CharField(max_length=16, unique=True)

    def __str__(self):
        return f"Tag: {self.name}"


class Image(models.Model):
    thing = models.ForeignKey(Thing, on_delete=models.CASCADE)
    tag = models.ForeignKey(ImageTag, on_delete=models.SET_NULL, blank=True, null=True)
    image = models.ImageField(upload_to='', null=True, blank=True)


