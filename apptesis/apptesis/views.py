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
from scipy.stats import norm
from scipy.optimize import newton

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
            es_primero = not Obra.objects.filter(proyecto=obra.proyecto).exists()
            obra.es_primero = es_primero
            obra.save()
            obra.deuda =  calcular_deuda(obra.duracion,obra.precio_agua,obra.dotacion_max,obra.es_primero,obra.proyecto,obra.id)
            obra.save()
            return redirect('nueva_obra')
    else:
        form = nuevaObraForm()

    return render(request, 'nuevaObra.html', {'form': form})

def nuevo_proyecto(request):
    if not request.user.is_authenticated:
        # Manejo de casos donde el usuario no está autenticado
        return redirect('login')
    if request.method == 'POST':
        form = nuevoProyectoForm(request.POST)
        if form.is_valid():
            obra = form.save(commit=False)
            obra.user = request.user
            obra.save()
            return redirect('nuevo_proyecto')
    else:
        form = nuevoProyectoForm()

    return render(request, 'nuevoProyecto.html', {'form': form})

def obras_existentes(request):
    if not request.user.is_authenticated:
        # Manejo de casos donde el usuario no está autenticado
        return redirect('login')
    obras = Obra.objects.filter(user=request.user)
    return render(request, 'myObras.html', {'obras': obras})

media_porcentual = 0.6
desviacion = 6.3
consumo_por_persona = 80
dias_habiles = 22
def calcular_deuda(duracion,precio,dotacion_max,es_primero,project,id):
    avances = []
    avances_meses = []
    avance_antes = 0
    max_avance = 0
    media = duracion * media_porcentual

    for i in range(1, duracion + 1):
        mes = i
        avance_acumulado = round(norm.cdf(mes, loc=media, scale=desviacion), 4)
        avance_mes = round(avance_acumulado - avance_antes, 4)
        avances_meses.append(avance_mes)
        avance_antes = avance_acumulado
        avances.append((mes, avance_acumulado, avance_mes))
        if avance_mes > max_avance and i > 1:
            max_avance = avance_mes

    dotaciones = []

    for i in range(duracion):
        mes = i + 1
        avance_acumulado, avance_mes = avances[i][1], avances[i][2]
        porcentaje = round(avances_meses[i] / max_avance * 100, 2)
        if i == 0:
            dotacion = round(dotacion_max * media_porcentual)
        else:
            dotacion = round(porcentaje * dotacion_max / 100)
        dotaciones.append(dotacion)
    if dotaciones:
        dotaciones[0] = round(media_porcentual * dotaciones[1])

    dotacion_total= sum(dotaciones)
    ahorro= dotacion_total*precio*dias_habiles*consumo_por_persona
    costos_fijos = {
        'desconectar_planta': 0,
        'retirar_planta': 0,
        'reinstalar_planta': 0,
        'cierre_techumbre': 1537828,
        'mantencion_completa': 825176,
        'mantencion_preventiva': 825176,
        'mantencion_mensual': 150032,
        'pastillas_cloro': 12000,
    }
    
    if es_primero:
        deuda_compra=16953616
    else:
        obra_anterior = Obra.objects.filter(proyecto=project, id__lt=id).order_by('-id').first()
        deuda_compra= -obra_anterior.deuda
        costos_fijos['cierre_techumbre']=0
        costos_fijos['reinstalar_planta']= 166020
        costos_fijos['retirar_planta']=140450
        costos_fijos['desconectar_planta']=30901

    costo_total=costos_fijos['reinstalar_planta']+costos_fijos['retirar_planta']+costos_fijos['cierre_techumbre']+costos_fijos['desconectar_planta']+costos_fijos['mantencion_completa']*(duracion//3)+costos_fijos['pastillas_cloro']*duracion+costos_fijos['mantencion_mensual']*duracion
    costo_final=costo_total+deuda_compra
    deuda_final=ahorro-costo_final
    if deuda_final>0:
        deuda_final=0
    return deuda_final


def obra_mas(request, obra_id):
    obra_seleccionada = get_object_or_404(Obra, pk=obra_id)
    avances = []
    avances_meses = []
    avance_antes = 0
    max_avance = 0
    media = obra_seleccionada.duracion * media_porcentual

    for i in range(1, obra_seleccionada.duracion + 1):
        mes = i
        avance_acumulado = round(norm.cdf(mes, loc=media, scale=desviacion), 4)
        avance_mes = round(avance_acumulado - avance_antes, 4)
        avances_meses.append(avance_mes)
        avance_antes = avance_acumulado
        avances.append((mes, avance_acumulado, avance_mes))
        if avance_mes > max_avance and i > 1:
            max_avance = avance_mes

    tuplas_completas = []

    for i in range(obra_seleccionada.duracion):
        mes = i + 1
        avance_acumulado, avance_mes = avances[i][1], avances[i][2]
        porcentaje = round(avances_meses[i] / max_avance * 100, 2)
        avance_acumulado_pct = f"{avance_acumulado * 100:.2f}%"
        avance_mes_pct = f"{avance_mes * 100:.2f}%"
        if i == 0:
            dotacion = round(obra_seleccionada.dotacion_max * media_porcentual)
        else:
            dotacion = round(porcentaje * obra_seleccionada.dotacion_max / 100)
        tuplas_completas.append({
            'mes': mes,
            'avance_acumulado': avance_acumulado_pct,
            'avance_mes': avance_mes_pct,
            'porcentaje': porcentaje,
            'dotacion': dotacion
        })
    if tuplas_completas:
        tuplas_completas[0]['dotacion'] = round(media_porcentual * tuplas_completas[1]['dotacion'])

    # Calcular los datos para la nueva tabla de consumo
    nueva_tabla = []
    ahorro_acumulado = 0
    precio_agua_por_litro = obra_seleccionada.precio_agua
    for i, tupla in enumerate(tuplas_completas):
        dotacion = tupla['dotacion']
        consumo_por_mes_litros = dotacion * consumo_por_persona * dias_habiles
        ahorro = consumo_por_mes_litros * precio_agua_por_litro
        ahorro_acumulado += ahorro
        nueva_tabla.append({
            'mes': tupla['mes'],
            'dotacion': dotacion,
            'consumo_por_persona': consumo_por_persona,
            'consumo_por_dias': consumo_por_persona * dias_habiles,
            'dias_habiles': dias_habiles,
            'consumo_por_mes_litros': consumo_por_mes_litros,
            'precio_agua_por_litro': precio_agua_por_litro,
            'ahorro': round(ahorro),
            'ahorro_acumulado': round(ahorro_acumulado)
        })

    # Calcular los datos para la nueva tabla de mantenimiento
    tabla_costos = []
    total_costos = 0
    for mes in range(obra_seleccionada.duracion + 1):
        costos = calcular_costo_mensual(mes,obra_seleccionada)
        costo_mensual = sum(costos.values())
        total_costos += costo_mensual
        tabla_costos.append({
            'mes': mes,
            'compra_planta': costos['compra_planta'],
            'desconeccion_planta': costos['desconectar_planta'],
            'retiro_planta': costos['retirar_planta'],
            'reinstalacion_planta': costos['reinstalar_planta'],
            'cierre_techumbre': costos['cierre_techumbre'],
            'mantencion_completa': costos['mantencion_completa'],
            'mantencion_preventiva': costos['mantencion_preventiva'],
            'mantencion_mensual': costos['mantencion_mensual'],
            'pastillas_cloro': costos['pastillas_cloro'],
            'costo_mensual': costo_mensual
        })
    
    flujo_caja = []
    flujo_tir =[]
    flujo_caja_acumulado = 0

    for mes in range(obra_seleccionada.duracion + 1):
        if mes == 0:
            ahorro_mes = 0
        else:
            ahorro_mes = nueva_tabla[mes-1]['ahorro']
        costo_mes = tabla_costos[mes]['costo_mensual']
        flujo_caja_mes = ahorro_mes - costo_mes
        flujo_caja_acumulado += flujo_caja_mes
        flujo_tir.append(flujo_caja_mes)
        flujo_caja.append({
            'mes': mes,
            'ahorro': ahorro_mes,
            'costo_mensual': costo_mes,
            'flujo_caja': flujo_caja_mes,
            'flujo_caja_acumulado': flujo_caja_acumulado
        })
    print(flujo_tir)
    tir = calcular_tir(flujo_tir)
    context = {
        'obra_seleccionada': obra_seleccionada,
        'tuplas_completas': tuplas_completas,
        'nueva_tabla': nueva_tabla,
        'ahorro_total': ahorro_acumulado,
        'tabla_costos': tabla_costos,
        'total_costos': total_costos,
        'flujo_caja': flujo_caja,
        'tir': tir
    }

    return render(request, 'obraMas.html', context)

def calcular_costo_mensual(mes,obra):
    # Define los costos fijos según sea necesario
    if obra.es_primero:
        costos_fijos = {
            'compra_planta': 16953616,
            'desconectar_planta': 0,
            'retirar_planta': 0,
            'reinstalar_planta': 0,
            'cierre_techumbre': 1537828,
            'mantencion_completa': 825176,
            'mantencion_preventiva': 825176,
            'mantencion_mensual': 150032,
            'pastillas_cloro': 12000,
        }
    else:
        obra_anterior = Obra.objects.filter(proyecto=obra.proyecto, id__lt=obra.id).order_by('-id').first()
        costos_fijos = { 
            'compra_planta': -obra_anterior.deuda,
            'desconectar_planta': 30901,
            'retirar_planta': 140450,
            'reinstalar_planta': 166020,
            'cierre_techumbre': 0,
            'mantencion_completa': 825176,
            'mantencion_preventiva': 825176,
            'mantencion_mensual': 150032,
            'pastillas_cloro': 12000,
        }
    costos = {
        'compra_planta': 0,
        'desconectar_planta': 0,
        'retirar_planta': 0,
        'reinstalar_planta': 0,
        'cierre_techumbre': 0,
        'mantencion_completa': 0,
        'mantencion_preventiva': 0,
        'mantencion_mensual': 0,
        'pastillas_cloro': 0,
    }

    if mes == 0:
        costos['compra_planta'] = costos_fijos['compra_planta']
        costos['desconectar_planta'] = costos_fijos['desconectar_planta']
        costos['retirar_planta'] = costos_fijos['retirar_planta']
        costos['reinstalar_planta'] = costos_fijos['reinstalar_planta']
        costos['cierre_techumbre'] = costos_fijos['cierre_techumbre']

    if mes % 6 == 0 and mes!=0:
        costos['mantencion_completa'] = costos_fijos['mantencion_completa']

    if mes % 6 == 3:
        costos['mantencion_preventiva'] = costos_fijos['mantencion_preventiva']
    if mes>0:
        costos['mantencion_mensual'] = costos_fijos['mantencion_mensual']
        costos['pastillas_cloro'] = costos_fijos['pastillas_cloro']

    return costos


# Import numpy financial package
import numpy_financial as npf

def calcular_tir(flujo_caja):
    irr = npf.irr(flujo_caja) * 100
    return irr