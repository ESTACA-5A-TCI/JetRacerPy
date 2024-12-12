# Stream RTSP sur Jetson Nano
Pour diffuser le flux vidéo de la caméra CSI du Jetson Nano via RTSP, l’approche la plus courante s’appuie sur GStreamer et le module **gst-rtsp-server**. Voici un guide détaillé :

### Prérequis

1. **Caméra CSI fonctionnelle** : Assurez-vous que votre caméra CSI est bien connectée au Jetson Nano et qu’elle fonctionne. Vous pouvez tester avec la commande :  
   ```bash
   gst-launch-1.0 nvarguscamerasrc ! nvoverlaysink
   ```  
   Cela devrait afficher un flux en direct sur l’écran.

2. **GStreamer et gst-rtsp-server** : Le Jetson Nano a déjà GStreamer installé par défaut. Le module `gst-rtsp-server` est souvent inclus, mais sinon, vous pouvez l’installer via les dépôts Ubuntu (par exemple `sudo apt-get install libgstrtspserver-1.0-dev`), ou utiliser l’exemple `test-launch` fourni.

### Méthode simple avec `test-launch`

`test-launch` est un outil fourni avec gst-rtsp-server qui permet de lancer rapidement un serveur RTSP à partir d’une ligne de commande GStreamer.

1. **Localisation de `test-launch`** : Sur le Jetson Nano, `test-launch` se trouve généralement dans `/usr/local/bin/` ou `/usr/bin/`. Vous pouvez le trouver avec :  
   ```bash
   which test-launch
   ```
   
   Si vous n’arrivez pas à le trouver, installez `gst-rtsp-server` :
   ```bash
   sudo apt-get install libgstrtspserver-1.0-dev
   ```
   Selon la version, `test-launch` peut être inclus dans les exemples du package source ou dans un paquet séparé. Dans ce cas, il est parfois nommé `test-launch-1.0` et placé dans `/usr/local/bin`.

2. **Lancer le serveur RTSP** : Utilisez une pipeline GStreamer qui capture le flux de la caméra CSI, l’encode en H.264, puis le transporte via RTSP. Par exemple :  
   ```bash
   test-launch "nvarguscamerasrc ! video/x-raw(memory:NVMM),width=1280,height=720,framerate=30/1 ! omxh264enc ! rtph264pay name=pay0 pt=96"
   ```
   
   Explications de la pipeline :
   - `nvarguscamerasrc` : Source pour la caméra CSI sur Jetson.
   - `video/x-raw(memory:NVMM),width=1280,height=720,framerate=120/1` : Définit la résolution et le framerate (120 pour un flux en temps réel).
   - `omxh264enc` : Encode la vidéo en H.264 (accéléré matériellement sur Jetson).
   - `rtph264pay name=pay0 pt=96` : Prépare le flux H.264 pour un transport RTP.

   Une fois lancée, cette commande démarre un serveur RTSP local, généralement accessible via :
   ```
   rtsp://<adresse_IP_du_Jetson>:8554/test
   ```

   Par défaut, `test-launch` utilise le port 8554 et le chemin `test`. Vous pouvez personnaliser cela dans la ligne de commande ou via des arguments supplémentaires.

### Méthode plus avancée

Si vous souhaitez une configuration plus avancée (authentification, multiples flux, etc.), vous pouvez :

- Créer un petit script en Python ou en C qui utilise la librairie `gst-rtsp-server` et définit un pipeline plus complexe.
- Gérer la configuration du pipeline (bitrate, format, etc.) via GStreamer.

Exemple minimal en Python (si vous avez les bindings GObject et GStreamer disponibles) :

```python
#!/usr/bin/env python3
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject

Gst.init(None)

class RTSPServer:
    def __init__(self):
        self.server = GstRtspServer.RTSPServer()
        self.factory = GstRtspServer.RTSPMediaFactory()
        self.factory.set_launch((
            "nvarguscamerasrc ! video/x-raw(memory:NVMM),width=1280,height=720,framerate=120/1 "
            "! omxh264enc ! rtph264pay name=pay0 pt=96"
        ))
        self.factory.set_shared(True)
        self.server.get_mount_points().add_factory("/test", self.factory)
        self.server.attach(None)

if __name__ == "__main__":
    server = RTSPServer()
    loop = GObject.MainLoop()
    loop.run()
```

Lancez ce script, puis ouvrez le flux dans VLC ou un autre client RTSP en pointant sur :
```
rtsp://<adresse_IP_du_Jetson>:8554/test
```

---

### Vérification du flux

Pour vérifier que tout fonctionne, utilisez un lecteur RTSP comme VLC depuis un autre ordinateur :

1. Ouvrez VLC → Media → Ouvrir un flux réseau.
2. Dans la barre d’adresse, entrez :  
   ```
   rtsp://<adresse_IP_du_Jetson>:8554/test
   ```
3. Lancez et vous devriez voir le flux vidéo en direct.

