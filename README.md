# Optimasol
Core logic module for the Optimasol project: smart solar energy routing and optimization for households.

pour mise a jous sur git :

git init 
git remote add origin https://github.com/Optimasol-Team/Optimasol-v1.0-MILP.git
git pull origin main --allow-unrelated-histories
git branch -M main
git add ...
git commit - m ""
git push -u origin main

pour activer l'environnement : env\Scripts\activate

librairie a installer : 
pymysql pulp paho-mqtt numpy requests pvlib python-dateutil schedule,

pour l'appli :
 streamlit,

interface communication
 Si type is None alors juste enoie des données normales,
 si type auth : alors tentative de connexion aller érifier que l'utilisateur existe et que mdp bon, 
 si type is new_user: alors créer un utilisateur