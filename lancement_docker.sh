sudo apt update && sudo apt upgrade -y
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker pi
git clone https://github.com/ton-username/Optimasol-v1.0-MILP.git
info "Installation de Mosquitto..."
sudo apt install mosquitto mosquitto-clients -y
sudo systemctl enable mosquitto

info "Configuration de Mosquitto..."
sudo bash -c 'cat > /etc/mosquitto/conf.d/optimasol.conf << EOF
listener 1883
allow_anonymous true
EOF'

info "Démarrage de Mosquitto..."
sudo systemctl start mosquitto
sudo systemctl status mosquitto --no-p
cd Optimasol-v1.0-MILP
sed -i 's|mysql:latest|mysql/mysql-server:8.0-arm64|g' docker-compose.yaml
docker-compose up -d