# Usar una imagen base de Python
FROM python:3.12-slim-bookworm

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de requerimientos primero y luego instalar las dependencias
COPY requirements.txt ./
RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt

# Establecer las variables de entorno
ENV FLASK_APP=app
ENV FLASK_RUN_HOST=0.0.0.0

# Exponer el puerto de Flask
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["flask", "run", "--debug"]