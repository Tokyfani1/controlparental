import json
import os
import platform
import subprocess
import time
import sys
import shutil
from typing import List, Dict

class SoftwareBlocker:
    def __init__(self):
        self.blocked_apps_file = "blocked_apps.json"
        self.blocked_apps = self._load_blocked_apps()
        self.system = platform.system()
        self.watcher_script = "app_watcher.py"
        self.startup_script = "app_blocker_startup.bat" if self.system == "Windows" else "app_blocker_startup.sh"
        
    def _load_blocked_apps(self) -> Dict[str, Dict]:
        """Charge les applications bloquées depuis le fichier JSON"""
        if not os.path.exists(self.blocked_apps_file):
            return {}
        try:
            with open(self.blocked_apps_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_blocked_apps(self):
        """Sauvegarde les applications bloquées dans le fichier JSON"""
        with open(self.blocked_apps_file, 'w') as f:
            json.dump(self.blocked_apps, f, indent=4)
    
    def _get_executable_name(self, app_name: str) -> str:
        """Génère un nom d'exécutable à partir du nom de l'application"""
        # Retire les caractères spéciaux et les espaces
        exe_name = ''.join(c.lower() for c in app_name if c.isalnum() or c.isspace())
        exe_name = exe_name.replace(' ', '')
        return exe_name
    
    def block_application(self, app_name: str, exe_names: List[str] = None) -> bool:
        """Bloque une application"""
        if not exe_names:
            # Si aucun nom d'exécutable n'est fourni, en générer un
            exe_names = [self._get_executable_name(app_name)]
        
        # Vérifier si l'application est déjà bloquée
        if app_name in self.blocked_apps:
            # Mettre à jour la liste des exécutables si nécessaire
            existing_exes = set(self.blocked_apps[app_name]['exe_names'])
            new_exes = set(exe_names)
            if not existing_exes.issuperset(new_exes):
                self.blocked_apps[app_name]['exe_names'] = list(existing_exes.union(new_exes))
                self._save_blocked_apps()
                return True
            return False
        
        # Ajouter la nouvelle application
        self.blocked_apps[app_name] = {
            'exe_names': exe_names,
            'blocked': True
        }
        self._save_blocked_apps()
        
        # Créer ou mettre à jour le script de surveillance
        self._create_watcher_script()
        
        # Installer le blocage au démarrage
        self._install_startup_script()
        
        return True
    
    def unblock_application(self, app_name: str) -> bool:
        """Débloque une application"""
        if app_name in self.blocked_apps:
            self.blocked_apps.pop(app_name)
            self._save_blocked_apps()
            
            # Recréer le script de surveillance avec les applications restantes
            self._create_watcher_script()
            
            return True
        return False
    
    def get_blocked_apps(self) -> List[Dict]:
        """Retourne la liste des applications bloquées"""
        return [{'name': k, **v} for k, v in self.blocked_apps.items()]
    
    def is_app_blocked(self, app_name: str) -> bool:
        """Vérifie si une application est bloquée"""
        return app_name in self.blocked_apps
    
    def check_and_block(self) -> List[str]:
        """Vérifie et bloque les applications en cours d'exécution"""
        if not self.blocked_apps:
            return []

        blocked_processes = []

        for app_name, data in self.blocked_apps.items():
            for exe in data['exe_names']:
                try:
                    if self.system == "Windows":
                        # Ajouter ".exe" à l'exécutable si nécessaire
                        exe_full = f"{exe}.exe" if not exe.lower().endswith(".exe") else exe
                        
                        # Vérifie si le processus est actif avec tasklist
                        result = subprocess.run(
                            f'tasklist /FI "IMAGENAME eq {exe_full}"',
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )

                        # Si le nom de l'exécutable apparaît dans la sortie, tuer le processus
                        if exe_full.lower() in result.stdout.lower():
                            subprocess.run(
                                f'taskkill /F /IM "{exe_full}"',
                                shell=True,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL
                            )
                            if app_name not in blocked_processes:
                                blocked_processes.append(app_name)

                    elif self.system in ["Darwin", "Linux"]:
                        # Recherche avec pgrep et exécute pkill
                        result = subprocess.run(
                            f'pgrep -fl "{exe}"',
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )

                        if result.stdout.strip():
                            subprocess.run(
                                f'pkill -f "{exe}"',
                                shell=True,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL
                            )
                            if app_name not in blocked_processes:
                                blocked_processes.append(app_name)
                except Exception as e:
                    print(f"Erreur lors du blocage de {app_name}: {e}")

        return blocked_processes


    def _create_watcher_script(self):
        """Crée un script Python qui surveille et bloque en continu les applications"""
        if not os.path.exists(os.path.dirname(self.watcher_script)) and os.path.dirname(self.watcher_script):
            os.makedirs(os.path.dirname(self.watcher_script))
            
        script_content = """
import json
import os
import platform
import subprocess
import time
import sys

def load_blocked_apps():
    blocked_apps_file = "blocked_apps.json"
    if not os.path.exists(blocked_apps_file):
        print(f"Fichier {blocked_apps_file} introuvable.")
        return {}
    try:
        with open(blocked_apps_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Erreur lors du chargement des applications bloquées: {e}")
        return {}

def check_and_block():
    system = platform.system()
    blocked_apps = load_blocked_apps()
    
    if not blocked_apps:
        return
    
    for app_name, data in blocked_apps.items():
        for exe in data['exe_names']:
            try:
                if system == "Windows":
                    subprocess.run(
                        f'taskkill /F /IM "{exe}*.exe"', 
                        shell=True, 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL
                    )
                elif system == "Darwin":  # macOS
                    subprocess.run(
                        f'pkill -f "{exe}"', 
                        shell=True, 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL
                    )
                elif system == "Linux":
                    subprocess.run(
                        f'pkill -f "{exe}"', 
                        shell=True, 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL
                    )
            except Exception as e:
                print(f"Erreur lors du blocage de {app_name} ({exe}): {e}")

def main():
    print("Surveillance des applications bloquées démarrée...")
    try:
        while True:
            check_and_block()
            time.sleep(2)  # Vérifier toutes les 2 secondes
    except KeyboardInterrupt:
        print("Surveillance arrêtée.")
    except Exception as e:
        print(f"Erreur: {e}")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
"""
        
        with open(self.watcher_script, 'w') as f:
            f.write(script_content)
    
    def _install_startup_script(self):
        """Installe un script de démarrage pour lancer le watcher au démarrage"""
        if self.system == "Windows":
            # Pour Windows, créer un script batch qui s'exécute au démarrage
            bat_content = f"""@echo off
start /min pythonw "{os.path.abspath(self.watcher_script)}"
"""
            with open(self.startup_script, 'w') as f:
                f.write(bat_content)
            
            # Créer un raccourci dans le dossier de démarrage
            startup_folder = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup")
            shutil.copy(self.startup_script, startup_folder)
            
            # Exécuter immédiatement
            try:
                subprocess.Popen(f'start /min pythonw "{os.path.abspath(self.watcher_script)}"', shell=True)
            except Exception as e:
                print(f"Erreur lors du lancement du script de surveillance: {e}")
                
        elif self.system == "Darwin":  # macOS
            # Pour macOS, créer un fichier plist pour launchd
            plist_path = os.path.expanduser("~/Library/LaunchAgents/com.parentalcontrol.appblocker.plist")
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.parentalcontrol.appblocker</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>{os.path.abspath(self.watcher_script)}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
"""
            os.makedirs(os.path.dirname(plist_path), exist_ok=True)
            with open(plist_path, 'w') as f:
                f.write(plist_content)
            
            # Charger le service
            try:
                subprocess.run(f'launchctl load {plist_path}', shell=True)
            except Exception as e:
                print(f"Erreur lors du chargement du service launchd: {e}")
                
        elif self.system == "Linux":
            # Pour Linux, créer un service systemd utilisateur
            service_dir = os.path.expanduser("~/.config/systemd/user")
            os.makedirs(service_dir, exist_ok=True)
            
            service_path = os.path.join(service_dir, "appblocker.service")
            service_content = f"""[Unit]
Description=App Blocker Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 {os.path.abspath(self.watcher_script)}
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
"""
            with open(service_path, 'w') as f:
                f.write(service_content)
            
            # Activer et démarrer le service
            try:
                subprocess.run('systemctl --user daemon-reload', shell=True)
                subprocess.run('systemctl --user enable appblocker.service', shell=True)
                subprocess.run('systemctl --user start appblocker.service', shell=True)
            except Exception as e:
                print(f"Erreur lors de l'activation du service systemd: {e}")
                
            # Exécuter immédiatement
            try:
                subprocess.Popen(f'python3 "{os.path.abspath(self.watcher_script)}" &', shell=True)
            except Exception as e:
                print(f"Erreur lors du lancement du script de surveillance: {e}")
                
    def start_watcher(self):
        """Démarre le script de surveillance des applications"""
        if self.system == "Windows":
            try:
                subprocess.Popen(f'start /min pythonw "{os.path.abspath(self.watcher_script)}"', shell=True)
                return True
            except Exception as e:
                print(f"Erreur lors du lancement du script de surveillance: {e}")
                return False
        elif self.system in ["Darwin", "Linux"]:
            try:
                subprocess.Popen(f'python3 "{os.path.abspath(self.watcher_script)}" &', shell=True)
                return True
            except Exception as e:
                print(f"Erreur lors du lancement du script de surveillance: {e}")
                return False
        return False