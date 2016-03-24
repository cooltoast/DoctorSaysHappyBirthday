from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

# Create your views here.
def login(request):
    return render(request, 'happybirthday/login.html', {'redirect_uri':settings.REDIRECT_URI, 'client_id':settings.CLIENT_ID, 'scope':'patients:summary:read'})

def doctor(request):
    code = request.GET.get('code', None)
    return render(request, 'happybirthday/doctor.html', {'code':code})
