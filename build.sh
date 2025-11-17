#!/usr/bin/env bash
# exit on error
set -o errexit

# Instala las dependencias de Python
pip install -r requirements.txt

# Instala las dependencias de Tailwind CSS y construye el archivo de estilos
python manage.py tailwind install
python manage.py tailwind build

# Recoge TODOS los archivos estáticos (incluyendo el styles.css recién creado)
python manage.py collectstatic --no-input
