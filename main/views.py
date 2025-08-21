from django.shortcuts import render

# Create your views here.
def startpage(request):
    return render(request, 'starPageClientes.html')
