# Optimasol
Core logic module for the Optimasol project: smart solar energy routing and optimization for households.

pour mise a jous sur git :
git remote add origin https://github.com/Optimasol-Team/Optimasol-v1.0-MILP.git

git init 
git pull origin main --allow-unrelated-histories
git branch -M main
git add ...
git commit -m ""
"git push -u origin main"
git commit-u "partie docker"      

pour activer l'environnement : env\Scripts\activate

librairie a installer : 
pymysql pulp paho-mqtt numpy requests pvlib python-dateutil schedule,

pour l'appli :
 streamlit,

interface communication
 Si type is "creation" alors envoie le router_id et le pwd,
 si typ et termine avec "/DATA" alors c'est juste ranger les infos
 si type est "demande" alors donne les infos nécessaires

 si type is new_user: alors créer un utilisateur