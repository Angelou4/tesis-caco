from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
"""
Creamos un formulario que contenga los campos correspondiente a
las variables que tendrán la clase.
"""
class LoginForm(forms.Form):
    username = forms.CharField(max_length=65)
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)

"""
Heredamos de UserCreationForm nos sirve solamente para crear el formulario
de registro de nuestra app.

Dentro de la clase Meta definimos a qué modelo estamos registrando usuarios
y además definimos cuales de sus atributos le permitiremos al usuario ingresar.
"""
class RegisterForm(UserCreationForm):
    class Meta:
        model=Persona
        fields = ['username','email','password1','password2']


class nuevaObraForm(forms.ModelForm):
    class Meta:
        model = Obra
        fields = ['obra','encargado','tamano','duracion', 'dotacion_max','precio_agua']