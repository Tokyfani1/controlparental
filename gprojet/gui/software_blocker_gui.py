import platform
import subprocess
import threading
import customtkinter as ctk
from tkinter import messagebox
from logic.software_blocker import SoftwareBlocker
import os

# Import pour Windows registry
if platform.system() == "Windows":
    import winreg

class SoftwareBlockerFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        
        self.blocker = SoftwareBlocker()
        self.software_list = []
        self.watcher_running = False

        self.create_widgets()
        self.populate_installed_software()
        
        # Démarrer le watcher en arrière-plan
        self.start_watcher_service()

    def create_widgets(self):
        """Crée l'interface utilisateur"""
        # Titre
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            title_frame,
            text="🚫 Blocage de Logiciels",
            font=("Helvetica", 24, "bold"),
            text_color="#3498DB"
        ).pack(side="left")
        
        # Bouton de vérification et indicateur de statut
        controls_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        controls_frame.pack(side="right")
        
        self.status_label = ctk.CTkLabel(
            controls_frame,
            text="✅ Surveillance active",
            font=("Helvetica", 12),
            text_color="#2ECC71"
        )
        self.status_label.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            controls_frame,
            text="Vérifier et Bloquer Maintenant",
            command=self.check_and_block_apps,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            font=("Helvetica", 14)
        ).pack(side="right")
        
        # Frame principal — couleur transparente explicitement
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, pady=10)
        
        # Section de sélection logicielle
        select_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        select_frame.pack(fill="x", pady=10, padx=10)

        ctk.CTkLabel(
            select_frame,
            text="Logiciel à bloquer :",
            font=("Helvetica", 14)
        ).pack(side="left", padx=5)

        # ComboBox pour la liste des logiciels installés
        self.software_combobox = ctk.CTkComboBox(select_frame, width=300, font=("Helvetica", 14))
        self.software_combobox.pack(side="left", padx=5)
        
        # Entrée pour le nom de l'exécutable
        exe_frame = ctk.CTkFrame(select_frame, fg_color="transparent")
        exe_frame.pack(side="left", padx=5)
        
        ctk.CTkLabel(
            exe_frame,
            text="Nom de l'exécutable (optionnel) :",
            font=("Helvetica", 12)
        ).pack(side="left", padx=5)
        
        self.exe_entry = ctk.CTkEntry(exe_frame, width=150, font=("Helvetica", 12))
        self.exe_entry.pack(side="left", padx=5)
        
        # Bouton pour bloquer le logiciel sélectionné
        ctk.CTkButton(
            select_frame,
            text="Bloquer",
            command=self.block_selected_software,
            fg_color="#3498DB",
            hover_color="#2980B9",
            font=("Helvetica", 14)
        ).pack(side="left", padx=5)

        # Bouton pour rafraîchir la liste
        ctk.CTkButton(
            select_frame,
            text="Rafraîchir la liste",
            command=self.populate_installed_software,
            fg_color="#3498DB",
            hover_color="#2980B9",
            font=("Helvetica", 14)
        ).pack(side="left", padx=10)

        # Liste des logiciels bloqués
        list_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        list_frame.pack(fill="both", expand=True, pady=10, padx=10)

        ctk.CTkLabel(
            list_frame,
            text="Logiciels bloqués :",
            font=("Helvetica", 16, "bold"),
            text_color="#ECF0F1"
        ).pack(anchor="w")

        # Textbox pour afficher les logiciels bloqués
        self.blocked_apps_listbox = ctk.CTkTextbox(
            list_frame,
            font=("Helvetica", 14),
            wrap="word",
            height=200,
            fg_color="#2C3E50"
        )
        self.blocked_apps_listbox.pack(fill="both", expand=True)

        # Bouton de suppression
        ctk.CTkButton(
            list_frame,
            text="Supprimer la sélection",
            command=self.remove_selected,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            font=("Helvetica", 14)
        ).pack(pady=10)

        # Initialisation de la liste des logiciels bloqués
        self.update_apps_list()

    def populate_installed_software(self):
        """Récupère et met à jour la liste des logiciels installés"""
        self.software_list = self.get_installed_software()
        self.software_combobox.configure(values=self.software_list)
        if self.software_list:
            self.software_combobox.set(self.software_list[0])

    def get_installed_software(self):
        """Récupère la liste des logiciels installés selon le système"""
        system = platform.system()
        software = []

        if system == "Windows":
            software = self._get_installed_software_windows()
        elif system == "Linux":
            software = self._get_installed_software_linux()
        elif system == "Darwin":
            software = self._get_installed_software_macos()
        else:
            software = []

        return sorted(set(software))

    def _get_installed_software_windows(self):
        """Récupère la liste des logiciels installés sur Windows via le registre"""
        software_list = []
        reg_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]
        for reg_path in reg_paths:
            try:
                reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                for i in range(winreg.QueryInfoKey(reg_key)[0]):
                    try:
                        sub_key_name = winreg.EnumKey(reg_key, i)
                        sub_key = winreg.OpenKey(reg_key, sub_key_name)
                        try:
                            name, _ = winreg.QueryValueEx(sub_key, "DisplayName")
                            if name and name.strip():
                                software_list.append(name.strip())
                        except (FileNotFoundError, OSError):
                            continue
                    except (FileNotFoundError, OSError):
                        continue
            except Exception as e:
                print(f"Erreur accès registre Windows {reg_path}: {e}")
        
        # Ajouter des applications système communes
        common_apps = ["Chrome", "Firefox", "Edge", "Discord", "Steam", "Epic Games", "Minecraft", "Fortnite", "Roblox"]
        software_list.extend(common_apps)
        
        return software_list

    def _get_installed_software_linux(self):
        """Récupère la liste des logiciels installés sur Linux (Debian/Ubuntu)"""
        software = []
        try:
            # Essayer d'abord avec dpkg (Debian/Ubuntu)
            output = subprocess.check_output(['dpkg', '-l'], universal_newlines=True)
            lines = output.splitlines()
            for line in lines[5:]:
                parts = line.split()
                if len(parts) >= 2:
                    software.append(parts[1])
        except Exception:
            try:
                # Essayer avec pacman (Arch Linux)
                output = subprocess.check_output(['pacman', '-Q'], universal_newlines=True)
                lines = output.splitlines()
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 1:
                        software.append(parts[0])
            except Exception:
                try:
                    # Essayer avec rpm (Fedora/CentOS)
                    output = subprocess.check_output(['rpm', '-qa'], universal_newlines=True)
                    software = output.splitlines()
                except Exception as e:
                    print("Erreur lors de la récupération des logiciels Linux:", e)
        
        # Ajouter des applications communes
        common_apps = ["firefox", "chromium", "chrome", "discord", "steam", "minecraft", "lutris"]
        software.extend(common_apps)
        
        return software

    def _get_installed_software_macos(self):
        """Récupère la liste des logiciels installés sur macOS"""
        software = []
        try:
            # Utiliser ls pour lister les applications dans /Applications
            output = subprocess.check_output(['ls', '/Applications'], universal_newlines=True)
            for line in output.splitlines():
                if line.endswith('.app'):
                    software.append(line[:-4])  # Supprimer le .app à la fin
        except Exception as e:
            print("Erreur lors de la récupération des logiciels macOS:", e)
        
        # Ajouter des applications communes
        common_apps = ["Firefox", "Chrome", "Discord", "Steam", "Minecraft"]
        software.extend(common_apps)
        
        return software
    def block_selected_software(self):
        """Bloque le logiciel sélectionné dans la combobox"""
        selected_software = self.software_combobox.get()
        custom_exe = self.exe_entry.get().strip()
        
        if not selected_software:
            messagebox.showinfo("Sélection requise", "Veuillez sélectionner un logiciel à bloquer.")
            return
        
        # Liste des exécutables courants pour les applications populaires
        common_executables = {
            'chrome': ['chrome.exe', 'googlechrome.exe'],
            'firefox': ['firefox.exe'],
            'discord': ['discord.exe'],
            'steam': ['steam.exe', 'steamwebhelper.exe'],
            # Ajouter d'autres applications courantes ici
        }
        
        # Préparer les noms d'exécutables
        exe_names = []
        if custom_exe:
            exe_names.append(custom_exe)
        
        # Ajouter les exécutables connus si l'application correspond
        app_lower = selected_software.lower()
        for app, exes in common_executables.items():
            if app in app_lower:
                exe_names.extend(exes)
        
        # Bloquer l'application
        if self.blocker.block_application(selected_software, exe_names):
            threading.Thread(target=self._block_and_notify, args=(selected_software, exe_names)).start()
            self.update_apps_list()
        else:
            messagebox.showinfo("Application déjà bloquée", f"{selected_software} est déjà dans la liste de blocage.")
        
        # Réinitialiser les champs
        self.software_combobox.set('')
        self.exe_entry.delete(0, 'end')

    def _block_and_notify(self, app_name, exe_names):
        """Bloque l'application et notifie l'utilisateur"""
        # Essayer de tuer le processus immédiatement
        blocked = False
        for exe in exe_names:
            if self._kill_process_by_name(exe):
                blocked = True
        
        if blocked:
            messagebox.showinfo("Application bloquée", f"{app_name} a été bloquée et fermée.")
        else:
            messagebox.showinfo("Application ajoutée", 
                            f"{app_name} a été ajoutée à la liste de blocage et sera fermée si elle est démarrée.")

    def _kill_process_by_name(self, process_name):
        """Tue un processus par son nom"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    f'taskkill /F /IM "{process_name}"', 
                    shell=True, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True
                )
                return "SUCCESS" in result.stdout or "avec succès" in result.stdout
            else:
                result = subprocess.run(
                    f'pkill -f "{process_name}"', 
                    shell=True, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE
                )
                return result.returncode == 0
        except Exception:
            return False

    def update_apps_list(self):
        """Met à jour la liste des logiciels bloqués dans la textbox"""
        self.blocked_apps_listbox.delete("1.0", "end")
        blocked_apps = self.blocker.get_blocked_apps()
        if not blocked_apps:
            self.blocked_apps_listbox.insert("end", "Aucun logiciel bloqué pour le moment.\n")
            return
        
        for app in blocked_apps:
            self.blocked_apps_listbox.insert("end", f"• {app['name']}\n")
            self.blocked_apps_listbox.insert("end", f"  Exécutables: {', '.join(app['exe_names'])}\n\n")

    def remove_selected(self):
        """Débloque le logiciel sélectionné dans la textbox"""
        try:
            selection = self.blocked_apps_listbox.selection_get()
        except Exception:
            try:
                # Essayer de récupérer la ligne courante si aucune sélection
                current_line = self.blocked_apps_listbox.get("insert linestart", "insert lineend")
                if current_line.startswith('• '):
                    selection = current_line
                else:
                    messagebox.showerror("Erreur", "Veuillez sélectionner un logiciel à débloquer.")
                    return
            except Exception:
                messagebox.showerror("Erreur", "Veuillez sélectionner un logiciel à débloquer.")
                return
                
        if not selection.startswith('• '):
            messagebox.showerror("Erreur", "Veuillez sélectionner un nom de logiciel (ligne commençant par •).")
            return
            
        app_name = selection.split('•')[1].strip()
        if messagebox.askyesno("Confirmation", f"Voulez-vous vraiment débloquer {app_name}?"):
            if self.blocker.unblock_application(app_name):
                messagebox.showinfo("Succès", f"{app_name} a été débloqué.")
                self.update_apps_list()
            else:
                messagebox.showerror("Erreur", f"Impossible de débloquer {app_name}!")

    def check_and_block_apps(self):
        """Vérifie et bloque les applications en cours d'exécution"""
        threading.Thread(target=self._check_and_block_thread).start()
        
    def _check_and_block_thread(self):
        """Thread qui vérifie et bloque les applications"""
        blocked = self.blocker.check_and_block()
        if blocked:
            messagebox.showinfo("Applications bloquées", 
                              f"Les applications suivantes ont été bloquées : {', '.join(blocked)}")
        else:
            messagebox.showinfo("Aucune application bloquée", 
                              "Aucune application en cours d'exécution n'a été bloquée.")
    
    def start_watcher_service(self):
        """Démarre le service de surveillance en arrière-plan"""
        success = self.blocker.start_watcher()
        if success:
            self.watcher_running = True
            self.status_label.configure(text="✅ Surveillance active", text_color="#2ECC71")
        else:
            self.watcher_running = False
            self.status_label.configure(text="❌ Surveillance inactive", text_color="#E74C3C")