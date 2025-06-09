# Environovalab System


## Descripción


## Requisitos


## Instrucciones para iniciar el servidor localmente
1. Clonar el repositorio
Primero, clona este repositorio en tu máquina local:
~~~
git clone
~~~
2. Inicia el entorno virtual
Navega al directorio del proyecto y ejecuta el siguiente comando para iniciar el entorno virtualc
~~~
python -m venv venv    
~~~
~~~
.\venv\Scripts\activate
~~~
3. Instalación de dependencias
Ejecuta el siguiente comando para instalar las dependencias necesarias:
~~~
pip install -r requirements.txt
~~~
4. Realiza las migraciones
Ejecuta el siguiente comando para realizar las migraciones necesarias:
~~~
python manage.py makemigrations
~~~
5. Aplica las migraciones
Ejecuta el siguiente comando para aplicar las migraciones necesarias:
~~~
python manage.py migrate
~~~
6. Levanta la aplicacion
Ejecuta el siguiente comando para levantar el backend:
~~~
python manage.py runserver  
~~~