from django.shortcuts import render, HttpResponse

# Create your views here.
from django.shortcuts import render
from clock.models import User

def adduser(request):
   if request.method == "POST":
      login = request.POST['login']
      password = request.POST['password']
      email = request.POST['email']
      country = request.POST['country']
      date_of_birth = request.POST['date_of_birth']
      newUser = User(login=login, password=password, email=email, country=country,
                     date_of_birth = date_of_birth, is_premium=False)
      newUser.save()
      return HttpResponse("<h2>Record Added Successfully</h2>")
   return render(request, "form.html")


def index(response):
    return HttpResponse("This is a home page <br>"
                        "For now, you may navigate to ./clock <br>"
                        "or to ./adduser")
