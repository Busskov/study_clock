from django.shortcuts import render, HttpResponse, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .serializers import TodoSerializer

from clock.UserManager import UserManager
from clock.models import User

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


class UserListApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the todo items for given requested user
        '''
        users = User.objects.filter(id = request.id)
        serializer = TodoSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''
        data = {
            'login': request.data.get('login'),
            'password': request.data.get('completed'),
            'id': request.id
        }
        serializer = TodoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)