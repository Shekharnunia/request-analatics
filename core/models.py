from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class WebRequest(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    host = models.CharField(max_length=1000)
    content_length = models.CharField(max_length=1000)
    content_type = models.CharField(max_length=1000)
    path = models.CharField(max_length=1000)
    method = models.CharField(max_length=50)
    uri = models.CharField(max_length=2000)
    status_code = models.IntegerField()
    user_agent = models.CharField(max_length=1000, blank=True, null=True)
    cookies = models.TextField(blank=True, null=True)
    headers = models.TextField(blank=True, null=True)
    get = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    client_ip = models.CharField(max_length=200, null=True, blank=True)