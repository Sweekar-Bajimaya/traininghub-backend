import uuid

from django.db import models

# Create your models here.

class DistributedAppKey(models.Model):
    """
    This model is used to provide key to access api
    """
    app_key = models.UUIDField(blank=True, null=True, unique=True)
    client_name = models.CharField(max_length=255)
    remarks = models.CharField(max_length=255, help_text='purpose of app_key. eg for Android, IOS')

    def __str__(self):
        return '{} -: {}'.format(self.client_name, self.app_key)

    def save(self, *args, **kwargs):
        if not self.app_key:
            self.app_key = uuid.uuid4().hex
        return super().save(*args, **kwargs)
