#!/bin/bash

echo "================================================"
echo "🚀 OPTIMASOL V1 - INSTALLATION ET LANCEMENT"
echo "================================================"

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 1. Vérification et installation de Python
info "Vérification de Python..."
if ! command -v python3 &> /dev/null; then
    warn "Python3 non trouvé, installation..."
    sudo apt update
    sudo apt install python3 python3-pip -y
else
    info "Python3 déjà installé"
fi

# 2. Mise à jour système
info "Mise à jour du système..."
sudo apt update
sudo apt upgrade -y

# 3. Installation et configuration de Mosquitto
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
sudo systemctl status mosquitto --no-pager

# 4. Installation des dépendances Python
info "Installation des dépendances Python..."
pip3 install pymysql ortools pulp watchdog paho-mqtt requests schedule

# 5. Installation de MariaDB
info "Installation de MariaDB..."
sudo apt install mariadb-server -y
sudo systemctl start mariadb
sudo systemctl enable mariadb

info "Sécurisation de MariaDB..."
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'optimasol';"
sudo mysql -e "DELETE FROM mysql.user WHERE User='';"
sudo mysql -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"
sudo mysql -e "DROP DATABASE IF EXISTS test;"
sudo mysql -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';"
sudo mysql -e "FLUSH PRIVILEGES;"

info "Création de la base de données..."
sudo mysql -e "CREATE DATABASE IF NOT EXISTS optimasol_db;"
sudo mysql -e "CREATE USER IF NOT EXISTS 'optimasol_user'@'localhost' IDENTIFIED BY 'optimasol_pass';"
sudo mysql -e "GRANT ALL PRIVILEGES ON optimasol_db.* TO 'optimasol_user'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"

# 6. Téléchargement du code source
info "Téléchargement du code OptimaSol..."
if [ ! -d "Optimasol-v1.0-MILP-main" ]; then
    wget -q https://github.com/Optimasol-Team/Optimasol-v1.0-MILP/archive/refs/heads/main.zip
    unzip -q main.zip
    rm main.zip
fi

cd Optimasol-v1.0-MILP-main

# 7. Import de la BDD existante
info "Recherche du fichier de base de données..."
if [ -f "bdd.sql" ]; then
    info "Import de bdd.sql..."
    mysql -u root -poptimasol optimasol_db < bdd.sql
elif [ -f "bdd_v2.sql" ]; then
    info "Import de bdd_v2.sql..."
    mysql -u root -poptimasol optimasol_db < bdd_v2.sql
else
    warn "Aucun fichier SQL trouvé, recherche dans le dossier..."
    SQL_FILE=$(find . -name "*.sql" -type f | head -1)
    if [ -n "$SQL_FILE" ]; then
        info "Import de $SQL_FILE..."
        mysql -u root -poptimasol optimasol_db < "$SQL_FILE"
    else
        error "Aucun fichier SQL trouvé dans le projet"
    fi
fi

# 8. Configuration des fichiers de config
info "Configuration des fichiers de configuration..."
mkdir -p data
if [ ! -f "data/bdd_config.txt" ]; then
    cat > data/bdd_config.txt << EOF
{
    "host": "localhost",
    "user": "optimasol_user",
    "password": "optimasol_pass",
    "database": "optimasol_db",
    "port": 3306
}
EOF
    info "Fichier de configuration BDD créé"
fi

# 9. Test du système
info "Test du système OptimaSol..."
if command -v python3 &> /dev/null; then
    info "Lancement des tests..."
    python3 test.py || warn "Tests avec avertissements"
else
    error "Python3 non disponible"
fi

echo "================================================"
info "🎉 INSTALLATION TERMINÉE !"
echo ""
info "Commandes disponibles :"
echo "  cd Optimasol-v1.0-MILP-main"
echo "  python3 main.py          # Lancer le système"
echo "  python3 test_complet.py  # Tests complets"
echo ""
info "Base de données :"
echo "  mysql -u root -poptimasol optimasol_db"
echo "================================================"