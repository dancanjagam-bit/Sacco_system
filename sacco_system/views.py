import os
from django.shortcuts import render

def frontend(request):
    # This will serve React's index.html
    return render(request, "index.html")
