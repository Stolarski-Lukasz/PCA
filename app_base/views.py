from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def home(request):
    return render(request, 'home.html')

@csrf_exempt
def documentation(request):
    return render(request, 'documentation.html')

@csrf_exempt
def tutorial(request):
    return render(request, 'tutorial.html')

@csrf_exempt
def contact(request):
    return render(request, 'contact.html')