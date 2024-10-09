from django.shortcuts import render, HttpResponse, redirect
from clock.models import User


class UserManager:
    def addUser(self, request):
        login = request.POST['login']
        password = request.POST['password']
        email = request.POST['email']
        country = request.POST['country']
        date_of_birth = request.POST['date_of_birth']
        newUser = User(login=login, password_hash=password, email=email, country=country,
                       date_of_birth=date_of_birth, is_premium=False)
        newUser.save()
        print(newUser.login, newUser.country)

    def getUser(self, id):
        return User.objects.get(pk=id)

    def deleteUser(self, id):
        user = User.objects.get(pk=id)
        user.delete()
        return HttpResponse("<h2>Record has been deleted</h2>")

    def updateUser(self, request):
        user = User.objects.get(id=id)

        if request.method == 'POST':
            login = request.POST['login']
            password = request.POST['password']
            email = request.POST['email']
            country = request.POST['country']
            date_of_birth = request.POST['date_of_birth']

            user.login = login
            user.password_hash = password
            user.email = email
            user.country = country
            user.date_of_birth = date_of_birth

            user.save()
            return HttpResponse("<h2>Record has been updated</h2>")

        return render(request, 'updateUserForm.html', context)