from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
# Create your models here.


class CustomUser(AbstractUser):
    uuid = models.UUIDField(
         default=uuid.uuid4,
         editable=False)
