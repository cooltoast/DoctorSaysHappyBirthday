from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import datetime, pytz, requests

BASE_URL = 'https://drchrono.com'

# Create your views here.
def login(request):
    return render(request, 'happybirthday/login.html', {'redirect_uri':settings.REDIRECT_URI, 'client_id':settings.CLIENT_ID, 'scope':'patients:summary:read'})

def doctor(request):
    error = request.GET.get('error')
    if (error is not None):
        #return render(request, 'happybirthday/error.html', {'message':error})
        raise ValueError('Error authorizing application: %s' % error)

    requestData = {
        'code': request.GET.get('code'),
        'grant_type': 'authorization_code',
        'redirect_uri': settings.REDIRECT_URI,
        'client_id': settings.CLIENT_ID,
        'client_secret': settings.CLIENT_SECRET
    }

    response = requests.post('%s/o/token/' % BASE_URL, data=requestData)
    response.raise_for_status()
    data = response.json()

    access_token = data['access_token']
    refresh_token = data['refresh_token']
    expires_timestamp = datetime.datetime.now(pytz.utc) + datetime.timedelta(seconds=data['expires_in'])
    # save to db

    headers = {
          'Authorization': 'Bearer %s' % access_token
    }

    response = requests.get('%s/api/users/current' % BASE_URL, headers=headers)
    response.raise_for_status()
    data = response.json()

    # save to db
    doctor_id = data['id']
    username = data['username']

    patients = []
    patients_url = '%s/api/patients_summary' % BASE_URL
    while patients_url:
      data = requests.get(patients_url, headers=headers).json()
      patients.extend(data['results'])
      patients_url = data['next'] # A JSON null on the last page

    return render(request, 'happybirthday/doctor.html', {'patients':patients})

