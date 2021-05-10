from django.shortcuts import render

# Create your views here.

# ••• Esto es para que django encuentre nuestro template nuevo
def index(request):
    return render(request, 'index.html')