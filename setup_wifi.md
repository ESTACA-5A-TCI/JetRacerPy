
# Utilisation script setup_wifi_access_point:

#### 1. Configurer un point d'accès Wi-Fi :
```bash
python script.py --ip-base 192.168.4.1 --ssid MyAccessPoint --password SecurePassword
```

#### 2. Configurer un client Wi-Fi :
```bash
python script.py --ssid MyWiFiNetwork --password WiFiPassword --configure-client
```

#### 3. Ajouter un code de pays pour une configuration client :
```bash
python script.py --ssid MyWiFiNetwork --password WiFiPassword --country US --configure-client
```