# Explication de la représentation des données des boxs dans Netbox

## Interfaces

Chaque box présente plusieurs interfaces :

* eth0.65 : vlan 65 (pour les adresses lien local constituées à partir de la mac)
* eth0.101 : vlan 101 pour les adhérents télécommiens
* eth0.102 : vlan 102 pour les adhérents non-télécommiens
* lan1 / lan2 / lan3 : ports éthernets physique à l'arrière de la box
* wlan : port éthernet physique à l'arrière de la box
* wlan0 : **le réseau wifi du possesseur de la box** (adhérent fibre), aussi appelé *main user* dans le code
* wlan1 : réseau wifi du premier adhérent wifi
* wlan2 : réseau wifi du deuxième adhérent wifi
* wlan3,4, etc : idem

## Lien entre wlans et ip

Chaque utilisateur possède un wlan qui lui est propre avec un ssid (ex : "Rezel-Thorium") contenant son User Network ID (ex : "Thorium").
Chaque utilisateur possède également une ip publique sur le vlan 101 ou 102.
Pour faire le lien entre le wlan et l'adresse ip, on met dans le custom field "Linked WLAN" de l'adresse ip le wlan associé. Ceci doit être fait pour TOUTES les adresses ip (pas rétro-compatible)

## NAT

La définition des règles de NAT se fait dans les adresses ip publiques : on leur associe une adresse ip privée (ex : "192.168.0.0/24" ou "192.168.1.0/24") via le champ "NAT inside"

## PAT

Il n'y a pas de moyen natif à Netbox de définir les règles de PAT.
Elles sont donc définies comme des services sur les box. On crée un nouveau service par règle de PAT.
On remplit les champs ainsi :

* Protocol : le protocole choisi (tcp, udp)
* ipaddresses : uniquement l'adresse ip outside (publique)
* ports : uniquement le port public
* Inside IP Address (dans les customs fields) : l'adress ip privée
* Inside Port (dans les customs fields) : le port privé