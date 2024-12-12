# Exécuter un script Python automatiquement au démarrage
Sur un **Jetson Nano**, basé sur une distribution Linux (souvent Ubuntu), la méthode recommandée pour exécuter un script Python au démarrage est d'utiliser **systemd**. Cela garantit que le script est géré correctement au démarrage du système et peut facilement être configuré pour redémarrer en cas de problème.

### Étapes pour utiliser **systemd** :

1. **Créer un fichier de service systemd** :
   ```bash
   sudo nano /etc/systemd/system/votre_script.service
   ```

2. **Ajouter la configuration suivante** dans le fichier :
   ```ini
   [Unit]
   Description=Script Python pour Jetson Nano
   After=network.target

   [Service]
   ExecStart=/usr/bin/python3 /chemin/vers/votre_script.py
   Restart=always
   User=nom_utilisateur
   Environment="DISPLAY=:0" "XAUTHORITY=/home/nom_utilisateur/.Xauthority"

   [Install]
   WantedBy=multi-user.target
   ```

   **Explication des paramètres :**
   - `ExecStart` : Indique le chemin complet de l'interpréteur Python et du script.
   - `Restart` : Redémarre le service en cas de problème.
   - `User` : L'utilisateur sous lequel le script s'exécutera.
   - `Environment` : Définit des variables d'environnement nécessaires pour accéder à l'interface graphique, utile pour les applications affichant des fenêtres.

3. **Recharger systemd pour prendre en compte le nouveau service** :
   ```bash
   sudo systemctl daemon-reload
   ```

4. **Activer le service pour qu'il démarre automatiquement au boot** :
   ```bash
   sudo systemctl enable votre_script.service
   ```

5. **Tester le service immédiatement** :
   ```bash
   sudo systemctl start votre_script.service
   ```

6. **Vérifier l'état du service** pour s'assurer qu'il fonctionne correctement :
   ```bash
   sudo systemctl status votre_script.service
   ```

---

### Points spécifiques au Jetson Nano :
- Si votre script utilise la GPU pour des tâches comme TensorFlow ou PyTorch, assurez-vous que les dépendances CUDA sont correctement initialisées dans votre environnement.
- Pour les scripts nécessitant une interface graphique (par exemple, pour afficher des résultats), configurez la variable `DISPLAY` comme indiqué dans le fichier `systemd`.

