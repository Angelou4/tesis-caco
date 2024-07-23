from django.contrib.auth.models import AbstractUser
from django.db import models


class Persona(AbstractUser):
    """
    Hereda los atributos de AbstractUser
    [username, password, email, first_name, last_name, ...]
    Además, hereda todas las funcionalidades: autentificación,
    logout, encriptado de contraseñas, etc.
    """
    
    def __str__(self):
        return self.first_name + ' ' + self.last_name + f' ({self.username})'

class Proyecto(models.Model):
    nombre = models.CharField(max_length=100)
    # Otros campos de Proyecto si los hay

    def __str__(self):
        return self.nombre

tamaños = [('Pequeña', 'Pequeña'), ('Mediana', 'Mediana'), ('Grande', 'Grande')]

class Obra(models.Model):
    user = models.ForeignKey(Persona, on_delete=models.CASCADE)
    encargado = models.CharField(max_length=30)
    obra = models.CharField(max_length=30)
    tamano = models.CharField(max_length=30, choices=tamaños)
    duracion = models.IntegerField()
    dotacion_max = models.IntegerField()
    precio_agua = models.FloatField()
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, null=True)
    es_primero = models.BooleanField(default=False)
    deuda = models.IntegerField(default=0)
    

    def __str__(self):
        return f'{self.obra} ({self.encargado})'