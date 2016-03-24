from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import datetime, pytz, requests

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

    response = requests.post('https://drchrono.com/o/token/', data=requestData)
    response.raise_for_status()
    data = response.json()

    access_token = data['access_token']
    refresh_token = data['refresh_token']
    expires_timestamp = datetime.datetime.now(pytz.utc) + datetime.timedelta(seconds=data['expires_in'])
    # save to db
    return render(request, 'happybirthday/doctor.html', {})
