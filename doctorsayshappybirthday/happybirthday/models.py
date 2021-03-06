from __future__ import unicode_literals

from django.db import models
import datetime

# Create your models here.
class Doctor(models.Model):
  name = models.CharField(max_length=200)
  doctor_id = models.IntegerField(default=0)
  access_token = models.CharField(max_length=200)
  refresh_token = models.CharField(max_length=200)
  expires_timestamp = models.DateTimeField()


class Patient(models.Model):
  name = models.CharField(max_length=200)
  patient_id = models.IntegerField(default=0)
  date_of_birth = models.DateTimeField(default=datetime.datetime.now)
  email = models.EmailField(default=None)
  doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
