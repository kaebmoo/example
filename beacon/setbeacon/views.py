from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to my Beacon API!")

class SetBeaconsView(APIView):
    def post(self, request):
        received_data = request.data
        print(received_data)  # พิมพ์ข้อมูลออกทางหน้าจอ
        return Response(received_data, status=status.HTTP_200_OK)
