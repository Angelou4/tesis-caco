from django.http import *
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, get_object_or_404
from .models import Obra
from apptesis.forms import *
from django.http import *
from apptesis.models import * 
from apptesis.urls import * 

# Create your views here.

# Registro 'register/'
def sign_up(request):
    if request.method == 'GET':
        # Estos formularios los creamos nosotros en el archivo forms.py
        form = RegisterForm()
        return render(request, 'users/register.html', { 'form': form })

    if request.method == 'POST':
        form = RegisterForm(request.POST) 
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request, 'You have singed up successfully.')
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'users/register.html', {'form': form})
        
# Login 'login/'    
def sign_in(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request,'users/login.html', {'form': form})
    
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request,username=username,password=password)
            if user:
                login(request, user)
                messages.success(request,f'Hi {username.title()}, welcome back!')
                return redirect('home')
        
        # form is not valid or user is not authenticated
        messages.error(request,f'Invalid username or password')
        return render(request,'users/login.html',{'form': form})

# Logout 'logout/'
def sign_out(request):
    logout(request)
    return HttpResponseRedirect('/home')

def home(request):
    if request.method == 'GET':
        return render(request,'home.html')
    
def nueva_obra(request):
    if not request.user.is_authenticated:
        # Manejo de casos donde el usuario no está autenticado
        return redirect('login')
    if request.method == 'POST':
        form = nuevaObraForm(request.POST)
        if form.is_valid():
            obra = form.save(commit=False)
            obra.user = request.user
            obra.save()
            return redirect('nuevaObra')
    else:
        form = nuevaObraForm()

    return render(request, 'nuevaObra.html', {'form': form})

def obras_existentes(request):
    if not request.user.is_authenticated:
        # Manejo de casos donde el usuario no está autenticado
        return redirect('login')
    obras = Obra.objects.filter(user=request.user)
    return render(request, 'myObras.html', {'obras': obras})

media_porcentual = 0.6
desviacion = 5

def obra_mas(request, obra_id):
    obra_seleccionada = get_object_or_404(Obra, pk=obra_id)
    avances = []
    avances_meses = []
    avance_antes = 0
    max_avance = 0

    # Primer bucle para calcular los avances
    for i in range(1, (obra_seleccionada.duracion) + 1):
        mes = i
        avance_acumulado = norm.cdf(mes, loc=media_porcentual, scale=desviacion)
        avance_mes = avance_acumulado - avance_antes
        avances_meses.append(avance_mes)
        avance_antes = avance_acumulado
        avances.append((mes, avance_acumulado, avance_mes))
        if avance_mes > max_avance:
            max_avance = avance_mes

    tuplas_completas = []

    # Segundo bucle para calcular porcentajes y dotaciones
    for i in range(obra_seleccionada.duracion):
        mes = i + 1
        avance_acumulado, avance_mes = avances[i][1], avances[i][2]
        porcentaje = round(avances_meses[i] / max_avance, 2)
        if i == 0:
            dotacion = round(obra_seleccionada.dotacion_max * media_porcentual)
        else:
            dotacion = round(porcentaje * obra_seleccionada.dotacion_max)
        tuplas_completas.append([mes, avance_acumulado, avance_mes, porcentaje, dotacion])

    context = {
        'obra_seleccionada': obra_seleccionada,
        'tuplas_completas': tuplas_completas
    }

    return render(request, 'template.html', context)