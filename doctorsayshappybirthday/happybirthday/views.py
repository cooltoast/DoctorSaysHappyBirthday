from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import datetime, pytz, requests

from .models import Doctor, Patient

BASE_URL = 'https://drchrono.com'

# need more than patients_summary scope to get patient's email
patientScope = 'patients:read'


# Create your views here.
def login(request):
    return render(request, 'happybirthday/login.html', {'redirect_uri':settings.REDIRECT_URI, 'client_id':settings.CLIENT_ID, 'scope':patientScope})

def doctor(request):
    error = request.GET.get('error')
    if (error is not None):
        raise ValueError('Error authorizing application: %s' % error)

    response = requests.post('%s/o/token/' % BASE_URL, data={
        'code': request.GET.get('code'),
        'grant_type': 'authorization_code',
        'redirect_uri': settings.REDIRECT_URI,
        'client_id': settings.CLIENT_ID,
        'client_secret': settings.CLIENT_SECRET
    })
    response.raise_for_status()
    data = response.json()

    access_token = data['access_token']
    refresh_token = data['refresh_token']
    expires_timestamp = datetime.datetime.now(pytz.utc) + datetime.timedelta(seconds=data['expires_in'])

    headers = {
          'Authorization': 'Bearer %s' % access_token
    }

    response = requests.get('%s/api/users/current' % BASE_URL, headers=headers)
    response.raise_for_status()
    data = response.json()

    doctor_id = data['doctor']
    username = data['username']


    # update if exists or create new
    params = {
      'name':username,
      'doctor_id':doctor_id,
      'access_token':access_token,
      'refresh_token':refresh_token,
      'expires_timestamp':expires_timestamp
    }
    d, doctorCreated = Doctor.objects.update_or_create(
      doctor_id=doctor_id,
      defaults=params
    )


    patients = []
    createdPatients = []
    # get /api/patients to retrieve email
    patients_url = '%s/api/patients' % BASE_URL
    while patients_url:
      data = requests.get(patients_url, headers=headers).json()
      patients.extend(data['results'])
      patients_url = data['next'] # A JSON null on the last page

    for patient in patients:
      full_name = patient['first_name'] + ' ' + patient['last_name']
      dobString = patient['date_of_birth'].replace('-','')
      dob = datetime.datetime.strptime(dobString,'%Y%m%d')
      timezoneAwareDob = pytz.timezone('America/Los_Angeles').localize(dob)
      patient_id = patient['id']

      # update if exists or create new
      params = {
        'name':full_name,
        'email':patient['email'],
        'date_of_birth':timezoneAwareDob,
        'patient_id':patient_id,
        'doctor':d,
      }
      p, patientCreated = Patient.objects.update_or_create(
        patient_id=patient_id,
        defaults=params
      )

      if patientCreated:
        # only add important info
        createdPatients.append(params)




    return render(request, 'happybirthday/doctor.html', {'doctor':username, 'doctor_created':doctorCreated, 'patients':createdPatients})

