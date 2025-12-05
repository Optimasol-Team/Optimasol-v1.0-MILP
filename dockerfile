
FROM python:3.12-slim

WORKDIR /app

# Installer les dépendances
RUN pip install pymysql pulp numpy paho-mqtt watchdog

# Le code sera monté via le volume dans docker-compose
# Donc pas besoin de COPY ici pour le développement

CMD ["python", "main.py"] 