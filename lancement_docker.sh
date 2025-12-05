
#!/bin/bash

# Mise à jour système
sudo apt update && sudo apt upgrade -y

# Installation Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker pi

# ★ Applique les nouveaux groupes sans redémarrage
newgrp docker << EONG

# Installation Mosquitto
echo "Installation de Mosquitto..."
sudo apt install mosquitto mosquitto-clients -y
sudo systemctl enable mosquitto

# Configuration Mosquitto
echo "Configuration de Mosquitto..."
sudo bash -c 'cat > /etc/mosquitto/conf.d/optimasol.conf << EOF
listener 1883
allow_anonymous true
EOF'

echo "Démarrage de Mosquitto..."    
sudo systemctl start mosquitto
sudo systemctl status mosquitto --no-pager

# Docker Compose

sed -i 's|mysql:latest|mysql/mysql-server:8.0-arm64|g' docker-compose.yaml

# ★ Vérifie que docker-compose est disponible
docker-compose --version

# Lancement des containers
docker compose up -d

echo "Vérification des containers en cours d'exécution..."
docker ps
EONG