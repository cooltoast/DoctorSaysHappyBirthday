from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from happybirthday.models import Doctor, Patient
from happybirthday.views import updatePatientList

import datetime, pytz, requests

class Command(BaseCommand):
  help = 'Sends birthday email and updates patient lists'

  def handle(self, *args, **options):
    updateDoctorsAndPatients()
    #getBirthdays()


def getBirthdays():
  today = datetime.datetime.today()
  return Patient.objects.filter(date_of_birth__month=today.month, date_of_birth__day=today.day)

def sendEmails():
  bdayPatients = getBirthdays()
  if not bdayPatients:
    return

  for patient in bdayPatients:
    if not patient.email:
      return
    '''
    send_mail('Happy Birthday from Dr. %s!' % patient.doctor.name,
              'Dear %s,\n\nHappy birthday from Dr. %s!' % (patient.name, patient.doctor.name),
              'mpdrchrono@gmail.com',
              [patient.email],
              fail_silently=False)
    '''


def updateDoctorsAndPatients():
  utcNow = datetime.datetime.now(pytz.utc)
  for doctor in Doctor.objects.all():
    # refresh any expired access tokens
    if (doctor.expires_timestamp < utcNow):
      response = requests.post('https://drchrono.com/o/token/', data={
          'refresh_token': doctor.refresh_token,
          'grant_type': 'refresh_token',
          'client_id': settings.CLIENT_ID,
          'client_secret': settings.CLIENT_SECRET
      })

      response.raise_for_status()
      data = response.json()

      access_token = data['access_token']
      expires_timestamp = datetime.datetime.now() + datetime.timedelta(seconds=data['expires_in'])
      timezoneAwareExpiresTimestamp = pytz.timezone('America/Los_Angeles').localize(expires_timestamp)

      # update
      doctor.access_token = access_token
      doctor.expires_timestamp = expires_timestamp
      doctor.save()

    # update patient list
    createdPatients = updatePatientList(doctor)
    #print 'created patients: %s' % createdPatients

