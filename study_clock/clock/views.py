from django.shortcuts import render, HttpResponse
from clock.models import User

# Create your views here.

def index(response):
    user = User(login="BolTss", password_hash="hash", date_of_birth ="15/10/2004", email="bol@gmail.com",
                country="by", is_premium=False)
    print("hello, this is ", user.login)
    obj = User.objects.get(id=1)

    return HttpResponse(
        'Clock is about to be here soon...' \
        'In the meantime, \
        you may think about \
        buying a premium subscription \
        to encourage further development')
