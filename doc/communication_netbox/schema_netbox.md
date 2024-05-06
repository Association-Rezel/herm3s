# Explication de la représentation des données des boxs dans Netbox

## Overview des changements

### Interfaces

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

### Lien entre wlans et ip

Chaque utilisateur possède un wlan qui lui est propre avec un custom field indiquant son User Network Id (unet_id).
Chaque utilisateur possède également une ip publique sur le vlan 101 ou 102.
Pour faire le lien entre le wlan et l'adresse ip, on met dans le custom field "Linked WLAN" de l'adresse ip le wlan associé. Ceci doit être fait pour TOUTES les adresses ip **(pas rétro-compatible)**

### NAT

La définition des règles de NAT se fait dans les adresses ip publiques : on leur associe une adresse ip privée (ex : "192.168.0.0/24" ou "192.168.1.0/24") via le champ "NAT inside"

### PAT

Il n'y a pas de moyen natif à Netbox de définir les règles de PAT.
Elles sont donc définies comme des services sur les box. On crée un nouveau service par règle de PAT.
On remplit les champs ainsi :

* Protocol : le protocole choisi (tcp, udp)
* ipaddresses : uniquement l'adresse ip outside (publique)
* ports : uniquement le port public
* Inside IP Address (dans les customs fields) : l'adress ip privée
* Inside Port (dans les customs fields) : le port privé

### A SUPPRIMER DANS LE NETBOX LEGACY

Le custom field `local id` sur les wireless lans était présent et required mais jamais utilisé. Il faut absolument le supprimer **sans quoi la validation de données va échouer**.

## Détails de ce qu'il faut ajouter lors de la création d'une box

### Prérequis

Ces prérequis sont nécessaires pour que la création de boxs soit possible, ils doivent être définis une seule fois avec des valeurs particulières et il n'est donc par pertinent de les redéfinir ici. On donnera seulement la liste minimale des catégories devant être présentes pour qu'herm3s fonctionne :

* device types (ac2350)
* device roles (box)
* all customs fields
* sites (au moins un)

### Création d'une box

Elements obligatoires pour instancier une box :

1. Name : (convention) BOX KLEY-XXX
2. Device Role : box
3. Device Type : ac2350
4. Site : peu importe
5. Status : active

Il faut ensuite ajouter/éditer les interfaces suivantes :

    Ajouter D'ABORD tous les WLANs (pas les interfaces, les wlans) nécessaires (un par utilisateur de la box)
      1. éditer le wlan0
         1. MAC Address
         2. Définir un WLAN et l'associer. Pour le définir :
            1. SSID : convention : Rezel-unetid
            2. Pre-shared key : (mot de passe)
            3. Dans les custom fields : le **unet_id** de l'utilisateur associé
      2. Ajouter les autres interface wlans qui doivent posséder les attributs :
         1. Device : le device 
         2. 

1. etho.65
   1. MAC Address
   2. Définir une Ip Address puis l'ajouter à l'interface. Pour définir l'Ip
      1. Address : adresse ipv6 ou v4 (avec mask)
      2. Dans interface assignement : device/interface : eth0.65
      3. Dans les customs fields : Linked WLAN : le WLAN (et pas unet_id) associé au user associé à l'ip
2. eth0.101 et eth0.102 :
   1. MAC Address
   2. Définir les adresses ip et les ajouter aux interfaces (pour les définir, suivre le même processus que pour eth0.65)
3. éditer l'interface wlan0
   1. MAC Address
   2. Associer le bon WLAN. Pour le définir :
   3. SSID : convention : Rezel-unetid
   4. Pre-shared key : (mot de passe)
   5. Dans les custom fields : le **unet_id** de l'utilisateur associé
4. Ajouter les autres interface wlans qui doivent posséder les attributs :
   1. Device : la box que l'on est en train de créer
   2. Name : wlan{1,2,3,4,5,6,7,8,9,10}
   3. Type : IEEE 802.11ac
   4. MAC Address
   5. le bon WLAN associé