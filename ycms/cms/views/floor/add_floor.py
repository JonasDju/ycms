from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from ...models import Floor

def add_floor(request):
    if request.method == "POST":
       
        return redirect("floor")
