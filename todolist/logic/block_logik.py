import psutil
import time

class ProcessBlocker:
    def __init__(self):
        self.blocked_processes = []  # Liste des noms de processus à bloquer
        self.is_blocking_active = False  # État du blocage

    def add_blocked_process(self, process_name):
        """Ajoute un processus à la liste des processus bloqués."""
        if process_name.lower() not in [p.lower() for p in self.blocked_processes]:
            self.blocked_processes.append(process_name)

    def remove_blocked_process(self, process_name):
        """Supprime un processus de la liste des processus bloqués."""
        self.blocked_processes = [p for p in self.blocked_processes if p.lower() != process_name.lower()]

    def start_blocking(self):
        """Démarre le blocage des processus."""
        if self.is_blocking_active:
            return  # Déjà en cours
        self.is_blocking_active = True
        while self.is_blocking_active:
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'].lower() in [p.lower() for p in self.blocked_processes]:
                        proc.kill()  # Arrête le processus
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            time.sleep(5)  # Vérifie toutes les 5 secondes

    def stop_blocking(self):
        """Arrête le blocage des processus."""
        self.is_blocking_active = False