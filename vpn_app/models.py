from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.CharField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)


class Site(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    url = models.URLField()

class Statistics(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    page_transitions = models.IntegerField(default=0)
    data_sent = models.FloatField(default=0)
    data_received = models.FloatField(default=0)