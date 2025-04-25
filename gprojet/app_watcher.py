
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
