from django.shortcuts import render, HttpResponse, redirect

from clock.UserManager import UserManager
from clock.models import User

# Create your views here.
import time

def homePageRedirect(request):
    return redirect(homePage)
    # manager = UserManager()
    # #manager.deleteUser(2)
    # return HttpResponse('Clock is about to be here soon...<br>'
    #                     'In the meantime, you may think about buying a '
    #                     'premium subscription to encourage further '
    #                     'development <br>' + str(User.objects.exists()) + '<br>' + str(len(User.objects.all())))

def homePage(request):
    # user = User(login="BolTss", password_hash="hash", date_of_birth ="15/10/2004", email="bol@gmail.com",
    #             country="by", is_premium=False)
    # print("hello, this is ", user.login)
    # return HttpResponse('Clock is about to be here soon...\n'
    #                     'In the meantime, you may think about buying a premium subscription to encourage further development')
    return render(request, 'homePage.html')


def adduser(request):
   if request.method == "POST":
      user_manager = UserManager()
      user_manager.addUser(request=request)
      return HttpResponse("<h2>Record Added Successfully</h2>")
   return render(request, "addUserForm.html")