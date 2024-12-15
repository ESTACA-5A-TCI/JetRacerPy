# Script main.py 
Le script Python `main.py` permet de contrôler la JetRacer (voiture miniature basée sur Jetson Nano) via UDP et de diffuser un flux vidéo via RTSP :

---

## Vue d’ensemble

1. **Gestion du Wi-Fi** : La classe `WifiConfig` bascule entre le mode station (connexion à un réseau Wi-Fi existant) et le mode hotspot (création d’un point d’accès Wi-Fi).
2. **Serveur RTSP** : La classe `RTSPServer` utilise GStreamer pour capturer le flux de la caméra JetRacer, l’encoder en H.264, puis le diffuser sur un serveur RTSP.  
3. **Lecture des états électriques** : La classe `jetRacerStates` (non utilisée directement dans le code principal, mais référencée) lit les informations de tension et de courant via un capteur INA219.  
4. **Contrôleur JetRacer** : La classe `JetRacerController` gère les commandes reçues par UDP (démarrer/arrêter la voiture, ajuster la direction et l’accélération, activer/désactiver le streaming, configurer le Wi-Fi, etc.).
5. **Serveur UDP** : La classe `UDPServer` écoute les commandes sur un port UDP, transmet ces commandes au `JetRacerController`, et renvoie périodiquement l’état électrique au dernier client qui a envoyé une commande.

Le point d’entrée principal du script (`if __name__ == "__main__":`) crée un objet `JetRacerController`, initialise un `UDPServer`, puis lance un thread pour écouter les paquets UDP. Parallèlement, une boucle GObject (`GObject.MainLoop()`) gère le serveur RTSP.  

En résumé, ce script « attend » des commandes UDP, pilote la JetRacer en conséquence et diffuse éventuellement la caméra via RTSP.

---

## Détails des classes et fonctions

### 1. `WifiConfig`
Cette classe regroupe différentes méthodes statiques pour configurer le Wi-Fi sur la Jetson Nano :

- **`enable_station_mode(ssid, password)`**  
  - Arrête les services hostapd et dnsmasq (utilisés pour le hotspot).  
  - Bascule l’interface Wi-Fi `wlan0` en mode « station ».  
  - Met à jour la configuration via `nmcli` pour se connecter à un réseau existant (SSID et mot de passe).  
  - Redémarre wpa_supplicant et NetworkManager.  
  - Permet de rejoindre un réseau Wi-Fi externe.

- **`enable_hotspot_mode()`**  
  - Arrête wpa_supplicant et NetworkManager (car on ne veut plus utiliser le mode station).  
  - Configure une IP statique (192.168.4.1) sur l’interface Wi-Fi.  
  - Démarre hostapd et dnsmasq, qui mettent en place un point d’accès (SSID, DHCP, etc.).

### 2. `RTSPServer`
Cette classe encapsule un mini-serveur RTSP basé sur GStreamer :

- **`__init__()`**  
  - Crée un serveur RTSP `GstRtspServer.RTSPServer`.  
  - Configure un pipeline GStreamer qui :  
    1. Capture la vidéo depuis la caméra Jetson Nano (`nvarguscamerasrc`).  
    2. Fixe la résolution à 1280×720 et la cadence à 120 images/s.  
    3. Encode en H264 (`omxh264enc`).  
    4. Emballe ça sous forme de flux RTP H.264 (`rtph264pay`) prêt pour la diffusion RTSP.  
  - Monte cette « factory » sur l’URL `/test`. Autrement dit, le flux est accessible via `rtsp://<ip>:8554/test` par défaut.

- **`start_streaming()`** et **`stop_streaming()`**  
  - Attach/détach le serveur RTSP à la boucle GObject principale pour démarrer ou arrêter la diffusion.

### 3. `jetRacerStates`
Cette classe est censée gérer la lecture de la tension et du courant via un capteur INA219 (sous I2C). L’adresse est détectée automatiquement (0x41 ou 0x42). Le script calcule ensuite le pourcentage de batterie estimé.

- **`get_jetracer_state()`**  
  - Lit la tension (`bus_voltage`) et le courant (`current`).  
  - Calcule un pourcentage de batterie approximatif.  
  - Retourne une chaîne de la forme `"electric_state <power_mode> <voltage> <current> <battery_percent>"`.  
  - **Remarque** : Il y a une petite coquille dans le code : la ligne `self.ina.getgetCurrent_mA()` devrait probablement s’écrire `self.ina.getCurrent_mA()`.  

### 4. `JetRacerController`
Le cœur de la logique de contrôle de la JetRacer :

- **Initialisation**  
  - Crée une instance de la classe `NvidiaRacecar()` pour manipuler `throttle`, `steering`, etc.  
  - Crée un serveur RTSP (`RTSPServer`).  
  - Sauvegarde une instance `WifiConfig`.  
  - Initialise deux états : `running=True` (pour la boucle principale) et `can_receive_command=False` (pour bloquer les commandes tant que la voiture n’a pas reçu « start »).

- **`handle_command(command)`**  
  - Analyse la chaîne de commande reçue. Plusieurs commandes possibles :  
    - **`start`** : met la voiture en état « actif » (réception de commandes autorisées, `can_receive_command=True`).  
    - **`stop`** : arrête la voiture et bloque la réception de commandes (`can_receive_command=False`).  
    - **`throttle <valeur>`** / **`steering <valeur>`** : définit l’accélération ou la direction (uniquement si `can_receive_command` est vrai).  
    - **`control <throttle> <steering>`** : en une seule commande, définit accélération et direction.  
    - **`streamon` / `streamoff`** : démarre/arrête le serveur RTSP si `can_receive_command` est vrai.  
    - **`connect_wifi <SSID> <password>`** : bascule en mode station Wi-Fi.  
    - **`connect_hotspot`** : bascule en mode hotspot.  
    - **`set_throttle_gain <valeur>`**, **`set_steering_gain <valeur>`**, **`set_steering_offset <valeur>`** : modifie des coefficients internes du NvidiaRacecar.  
    - **`get_throttle_gain`**, **`get_steering_gain`**, **`get_steering_offset`** : renvoie les valeurs actuelles de ces paramètres.  
    - Si la commande est inconnue (ou si `can_receive_command=False`), renvoie un message d’erreur ou « Send 'start' command ».

- **`stop()`**  
  - Met `running=False`, arrête la voiture et stoppe le flux RTSP. Permet de quitter proprement le script.

### 5. `UDPServer`
Un serveur UDP qui tourne sur un port donné (8889 par défaut) :

- **`__init__(host, port, controller, send_interval=1.0)`**  
  - Crée un socket UDP pour écouter sur `(host, port)`.  
  - Mémorise l’objet `controller` (le `JetRacerController`) pour lui envoyer les commandes reçues.  
  - Conserve un `last_addr` pour savoir où renvoyer l’état périodique.  
  - `send_interval` définit la fréquence d’envoi de l’état de la voiture.

- **`start()`**  
  - Lance deux threads en parallèle :  
    - **Thread de réception** (`recv_thread`) : écoute les paquets UDP entrants, les décode et appelle `controller.handle_command(command)`. Enregistre `last_addr` pour les réponses.  
    - **Thread d’envoi** (`send_thread`) : envoie périodiquement l’état électrique de la voiture à `last_addr` toutes les `send_interval` secondes (par défaut toutes les 2 secondes dans le main).  

- **`recv_commands()`**  
  - Boucle infinie qui lit des paquets UDP jusqu’à ce que le `controller.running` soit `False`.  
  - Si une commande est reconnue et traitée, renvoie une réponse au même client.

- **`send_state_periodically()`**  
  - Toutes les `send_interval` secondes, envoie l’état électrique de la JetRacer au dernier client ayant communiqué.  
  - Appelle la méthode (potentielle) `controller.jetracer_states.get_jetracer_state()` (bien que dans le code, on ne voit pas forcément la création d’un objet `jetRacerStates` dans le contrôleur, donc ce passage est possiblement incomplet ou mal relié).

### 6. Point d’entrée principal

```python
if __name__ == "__main__":
    controller = JetRacerController()
    udp_server = UDPServer("0.0.0.0", 8889, controller, send_interval=2.0)

    # Thread pour démarrer le serveur UDP
    server_thread = threading.Thread(target=udp_server.start)
    server_thread.start()

    # Boucle GObject (nécessaire à GStreamer / RTSP)
    loop = GObject.MainLoop()
    loop.run()
```

- On instancie le contrôleur JetRacer (`controller`) et le serveur UDP (`udp_server`).  
- On lance un **thread** pour le serveur UDP, qui va démarrer `recv_commands` et `send_state_periodically`.  
- Simultanément, on exécute la boucle GObject (`GObject.MainLoop()`) qui est requise pour que le serveur RTSP fonctionne.  
- En cas d’interruption (CTRL+C), on arrête tout (`controller.stop()`).

---

## Conclusion

- **Ce script est un contrôleur complet pour une JetRacer**.  
- Il utilise **UDP** pour recevoir des commandes distantes (throttle, steering, etc.) et renvoyer périodiquement l’état électrique.  
- Il met en place un **flux RTSP** GStreamer accessible via l’URL `rtsp://<ip>:8554/test`.  
- Il gère la **configuration Wi-Fi** (mode station ou hotspot) pour le Jetson Nano.  

L’architecture repose majoritairement sur deux threads (un pour la réception de commandes UDP, un pour l’envoi d’états) et sur la boucle principale GObject (pour le RTSP). Chaque commande UDP est traitée de façon synchrone : le script répond directement au client et pilote la voiture en modifiant les attributs `throttle` et `steering`.  

Ainsi, pour **« comprendre »** le code :  
- Les **commandes UDP** (ex. « `throttle 0.3` ») sont envoyées par un client sur le port 8889.  
- Le **JetRacerController** applique la commande et renvoie une confirmation (ex. « `Throttle set to: 0.3` »).  
- Le **Serveur RTSP** permet, en parallèle, de **visionner en temps réel** la vidéo depuis la caméra JetRacer via un lecteur vidéo comme VLC (`rtsp://<adresse-IP>:8554/test`).  
- Le **mode Wi-Fi** peut être switché à la volée via des commandes du style « `connect_wifi <ssid> <password>` » ou « `connect_hotspot` ».

