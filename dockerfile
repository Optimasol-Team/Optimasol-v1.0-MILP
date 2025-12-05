
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential # pour installer numpy il faut installer ça avant
RUN pip install pymysql pulp numpy paho-mqtt watchdog

# Le code sera monté via le volume dans docker-compose
# Donc pas besoin de COPY ici pour le développement

CMD ["python", "main.py"] 