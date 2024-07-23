## Requisitos Previos

- Python 3.x instalado
- pip (el gestor de paquetes de Python) instalado

## Instrucciones de Configuración

1. Clona el repositorio del proyecto:

```bash
   git clone <URL-del-repositorio>
   cd <nombre-del-repositorio>
```
2. Insertar la proxima lineas de codigo en orden en el terminal
```console
python3 -m venv venv 
venv\Scripts\activate 
pip install -r requirements.txt 
cd apptesis 
python manage.py makemigrations 
python manage.py migrate 
python manage.py runserver 
```
3. Abre tu navegador web y navega a http://127.0.0.1:8000 para ver la aplicación en funcionamiento.
