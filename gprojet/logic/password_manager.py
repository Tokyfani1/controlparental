import os
import json
import hashlib
import secrets
import base64
import getpass
import customtkinter as ctk
from tkinter import messagebox

class PasswordManager:
    def __init__(self):
        self.password_file = "parental_auth.json"
        self.salt_length = 16
        self.password_data = self._load_password_data()
        
    def _load_password_data(self):
        """Charge les données du mot de passe depuis le fichier JSON"""
        if not os.path.exists(self.password_file):
            return {"is_set": False, "hash": None, "salt": None}
        try:
            with open(self.password_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"is_set": False, "hash": None, "salt": None}
    
    def _save_password_data(self):
        """Sauvegarde les données du mot de passe dans le fichier JSON"""
        with open(self.password_file, 'w') as f:
            json.dump(self.password_data, f)
    
    def is_password_set(self):
        """Vérifie si un mot de passe est déjà défini"""
        return self.password_data.get("is_set", False)
    
    def set_password(self, password):
        """Définit un nouveau mot de passe"""
        salt = secrets.token_bytes(self.salt_length)
        salt_b64 = base64.b64encode(salt).decode('utf-8')
        
        password_hash = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode('utf-8'), 
            salt, 
            100000  # Nombre d'itérations
        )
        hash_b64 = base64.b64encode(password_hash).decode('utf-8')
        
        self.password_data = {
            "is_set": True,
            "hash": hash_b64,
            "salt": salt_b64
        }
        
        self._save_password_data()
        return True
    
    def verify_password(self, password):
        """Vérifie si le mot de passe est correct"""
        if not self.is_password_set():
            return False
        
        salt = base64.b64decode(self.password_data["salt"])
        stored_hash = base64.b64decode(self.password_data["hash"])
        
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000  # Même nombre d'itérations que lors du hachage
        )
        
        return secrets.compare_digest(password_hash, stored_hash)


class PasswordDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, is_verification=False, callback=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x300")
        self.resizable(False, False)
        
        # Centre la fenêtre
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        self.grab_set()  # Rend la fenêtre modale
        
        self.callback = callback
        self.is_verification = is_verification
        self.result = False
        
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Icon
        ctk.CTkLabel(
            main_frame,
            text="🔒",
            font=("Helvetica", 36),
            text_color="#3498DB"
        ).pack(pady=(0, 10))
        
        if self.is_verification:
            # Message pour la vérification
            ctk.CTkLabel(
                main_frame,
                text="Entrez le mot de passe parental pour continuer",
                font=("Helvetica", 16),
                text_color="#ECF0F1"
            ).pack(pady=(0, 20))
            
            # Entrée de mot de passe
            self.password_entry = ctk.CTkEntry(
                main_frame,
                width=300,
                font=("Helvetica", 14),
                show="●"
            )
            self.password_entry.pack(pady=(0, 20))
            
            # Boutons
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(fill="x", pady=10)
            
            ctk.CTkButton(
                button_frame,
                text="Annuler",
                command=self.cancel,
                fg_color="#E74C3C",
                hover_color="#C0392B",
                font=("Helvetica", 14),
                width=100
            ).pack(side="left", padx=10)
            
            ctk.CTkButton(
                button_frame,
                text="Valider",
                command=self.validate_password,
                fg_color="#2ECC71",
                hover_color="#27AE60",
                font=("Helvetica", 14),
                width=100
            ).pack(side="right", padx=10)
            
        else:
            # Messages pour la définition
            ctk.CTkLabel(
                main_frame,
                text="Définir un mot de passe parental",
                font=("Helvetica", 16),
                text_color="#ECF0F1"
            ).pack(pady=(0, 20))
            
            # Entrée de mot de passe
            password_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            password_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                password_frame,
                text="Mot de passe:",
                font=("Helvetica", 14),
                width=120,
                anchor="e"
            ).pack(side="left", padx=5)
            
            self.password_entry = ctk.CTkEntry(
                password_frame,
                width=200,
                font=("Helvetica", 14),
                show="●"
            )
            self.password_entry.pack(side="left", padx=5)
            
            # Confirmation de mot de passe
            confirm_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            confirm_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                confirm_frame,
                text="Confirmation:",
                font=("Helvetica", 14),
                width=120,
                anchor="e"
            ).pack(side="left", padx=5)
            
            self.confirm_entry = ctk.CTkEntry(
                confirm_frame,
                width=200,
                font=("Helvetica", 14),
                show="●"
            )
            self.confirm_entry.pack(side="left", padx=5)
            
            # Boutons
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(fill="x", pady=(20, 10))
            
            ctk.CTkButton(
                button_frame,
                text="Annuler",
                command=self.cancel,
                fg_color="#E74C3C",
                hover_color="#C0392B",
                font=("Helvetica", 14),
                width=100
            ).pack(side="left", padx=10)
            
            ctk.CTkButton(
                button_frame,
                text="Valider",
                command=self.set_password,
                fg_color="#2ECC71",
                hover_color="#27AE60",
                font=("Helvetica", 14),
                width=100
            ).pack(side="right", padx=10)
    
    def validate_password(self):
        password = self.password_entry.get()
        if not password:
            messagebox.showerror("Erreur", "Veuillez entrer un mot de passe.")
            return
        
        self.result = password
        self.destroy()
        if self.callback:
            self.callback(password)
    
    def set_password(self):
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        if not password:
            messagebox.showerror("Erreur", "Veuillez entrer un mot de passe.")
            return
        
        if password != confirm:
            messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas.")
            return
        
        if len(password) < 4:
            messagebox.showerror("Erreur", "Le mot de passe doit contenir au moins 4 caractères.")
            return
        
        self.result = password
        self.destroy()
        if self.callback:
            self.callback(password)
    
    def cancel(self):
        self.result = None
        self.destroy()
        if self.callback:
            self.callback(None)