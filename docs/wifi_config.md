# Configurer et bascule entre le point d'accès et le réseau wifi
Pour réaliser cette solution, vous devez configurer votre Jetson Nano pour qu'il puisse fonctionner comme un point d'accès WiFi et en même temps permettre un basculement entre le mode "client WiFi" (connecté à un réseau existant) et "point d'accès WiFi". Ensuite, un script Python sur votre ordinateur Windows peut gérer la bascule à l'aide de sockets. Voici comment faire :

---

## 1. **Configurer le Jetson Nano comme point d'accès WiFi**
### Étapes :
1. **Installer `hostapd` et `dnsmasq` sur le Jetson Nano** :
    ```bash
    sudo apt update
    sudo apt install hostapd dnsmasq
    ```

2. **Configurer `hostapd`** :
    Créez ou éditez le fichier `/etc/hostapd/hostapd.conf` :
    ```bash
    sudo nano /etc/hostapd/hostapd.conf
    ```
    Ajoutez les paramètres suivants :
    ```plaintext
    interface=wlan0
    driver=nl80211
    ssid=JetsonAP
    hw_mode=g
    channel=6
    macaddr_acl=0
    auth_algs=1
    ignore_broadcast_ssid=0
    wpa=2
    wpa_passphrase=your_password
    wpa_key_mgmt=WPA-PSK
    rsn_pairwise=CCMP
    ```

3. **Configurer `dnsmasq`** :
    Créez ou éditez `/etc/dnsmasq.conf` :
    ```bash
    sudo nano /etc/dnsmasq.conf
    ```
    Ajoutez les lignes suivantes :
    ```plaintext
    interface=wlan0
    dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
    ```

4. **Configurer une IP statique pour `wlan0`** :
    Modifiez `/etc/network/interfaces.d/wlan0` :
    ```bash
    sudo nano /etc/network/interfaces.d/wlan0
    ```
    Ajoutez :
    ```plaintext
    auto wlan0
    iface wlan0 inet static
    address 192.168.4.1
    netmask 255.255.255.0
    ```
5. **Activer le service hostapd** :
    ```bash
    sudo systemctl unmask hostapd
    sudo systemctl enable hostapd
    ```
6. **démarrer le service hostapd** :
    ```bash
    sudo systemctl stop wpa_supplicant
    sudo systemctl stop network-manager
    sudo ifconfig wlan0 192.168.4.1 netmask 255.255.255.0 up
    sudo systemctl start hostapd
    sudo systemctl start dnsmasq
    ```

---

## 2. **Configurer le mode "client WiFi" sur Jetson Nano**
### Étapes :
1. **démarrer le service hostapd** :
    ```bash
    sudo systemctl stop hostapd
    sudo systemctl stop dnsmasq
    sudo ifconfig wlan0 down
    sudo ifconfig wlan0 up
    sudo systemctl start wpa_supplicant
    sudo systemctl start network-manager
    ```
3. **connecter sur un réseau**:
    Utilisez un gestionnaire de réseau (comme `nmcli`) pour basculer entre les réseaux WiFi.
    ```bash
    nmcli device wifi connect "WiFi_SSID" password "WiFi_password"
    ```





