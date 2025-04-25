from gui.calendar_gui import CalendarFrame
from gui.software_blocker_gui import SoftwareBlockerFrame 
import customtkinter as ctk
from logic.password_manager import PasswordManager, PasswordDialog

class ParentalControlApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Parental Control 🛡️")
        self.geometry("1200x800")
        self.minsize(1000, 600)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initialisation du gestionnaire de mot de passe
        self.password_manager = PasswordManager()
        
        # Vérification du mot de passe
        self.check_password()

        # Style configuration
        self.colors = {
            "sidebar": "#2C3E50",
            "sidebar_button": "#34495E",
            "sidebar_button_hover": "#2980B9",
            "main_bg": "#2C3E50",
            "card": "#34495E",
            "text": "#ECF0F1"
        }

        # Create layout
        self.create_sidebar()
        self.create_main_content()

    def check_password(self):
        """Vérifie si un mot de passe est défini, sinon en demande un"""
        if not self.password_manager.is_password_set():
            self.after(500, self.create_password_dialog)
        else:
            # Demander le mot de passe au démarrage
            self.after(500, self.verify_password)
    
    def create_password_dialog(self):
        """Crée un dialogue pour définir le mot de passe"""
        dialog = PasswordDialog(self, "Définir le mot de passe", False, self.handle_new_password)
    
    def handle_new_password(self, password):
        """Gère la création d'un nouveau mot de passe"""
        if password:
            self.password_manager.set_password(password)
            ctk.CTkLabel(
                self,
                text="✅ Mot de passe défini avec succès!",
                font=("Helvetica", 14),
                text_color="#2ECC71"
            ).place(relx=0.5, rely=0.1, anchor="center")
            # Faire disparaître le message après quelques secondes
            self.after(3000, lambda: [child.destroy() for child in self.winfo_children() 
                                    if isinstance(child, ctk.CTkLabel) and "✅" in child.cget("text")])
    
    def verify_password(self):
        """Vérifie le mot de passe avant d'autoriser l'accès"""
        dialog = PasswordDialog(self, "Contrôle Parental", True, self.handle_password_verification)
    
    def handle_password_verification(self, password):
        """Gère la vérification du mot de passe"""
        if password is None:  # L'utilisateur a annulé
            self.destroy()  # Fermer l'application
            return
            
        if self.password_manager.verify_password(password):
            # Mot de passe correct, continuer
            pass
        else:
            # Mot de passe incorrect
            ctk.CTkLabel(
                self,
                text="❌ Mot de passe incorrect!",
                font=("Helvetica", 14),
                text_color="#E74C3C"
            ).place(relx=0.5, rely=0.1, anchor="center")
            # Faire disparaître le message après quelques secondes
            self.after(2000, lambda: [child.destroy() for child in self.winfo_children() 
                                    if isinstance(child, ctk.CTkLabel) and "❌" in child.cget("text")])
            # Redemander le mot de passe
            self.after(2000, self.verify_password)

    def create_sidebar(self):
        """Create the left sidebar with navigation buttons"""
        sidebar = ctk.CTkFrame(self, width=200, fg_color=self.colors["sidebar"])
        sidebar.pack(side="left", fill="y", padx=0, pady=0)

        # App title
        ctk.CTkLabel(
            sidebar, 
            text="Parental Control",
            font=("Helvetica", 18, "bold"),
            text_color=self.colors["text"]
        ).pack(pady=(20, 30), padx=10)

        # Navigation buttons
        buttons = [
            ("📅 Calendar & Tasks", self.show_calendar),
            ("🚫 App Blocker", self.show_app_blocker),
            ("⏱️ Time Control", self.show_time_control),
            ("📊 Reports", self.show_reports),
            ("⚙️ Settings", self.show_settings)
        ]

        for text, command in buttons:
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                font=("Helvetica", 14),
                fg_color=self.colors["sidebar_button"],
                hover_color=self.colors["sidebar_button_hover"],
                anchor="w",
                command=command
            )
            btn.pack(fill="x", padx=10, pady=5)

    def create_main_content(self):
        """Create the main content area"""
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # Initialize with calendar view
        self.show_calendar()

    def clear_main_content(self):
        """Clear the main content area"""
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def show_calendar(self):
        self.clear_main_content()
        try:
            CalendarFrame(self.main_content)
        except Exception as e:
            ctk.CTkLabel(self.main_content, text=f"Erreur: {e}", text_color="red").pack(pady=20)

    def show_app_blocker(self):
        """Show the app blocker view"""
        # Vérifier le mot de passe avant d'accéder au blocage d'applications
        self.ask_password_then_execute(self._show_app_blocker)
    
    def _show_app_blocker(self):
        """Affiche la vue du bloqueur d'applications après vérification du mot de passe"""
        self.clear_main_content()
        SoftwareBlockerFrame(self.main_content)

    def show_time_control(self):
        """Show the time control view"""
        # Vérifier le mot de passe avant d'accéder au contrôle du temps
        self.ask_password_then_execute(self._show_time_control)
    
    def _show_time_control(self):
        """Affiche la vue du contrôle du temps après vérification du mot de passe"""
        self.clear_main_content()
        ctk.CTkLabel(
            self.main_content,
            text="Time Control - Coming Soon",
            font=("Helvetica", 24),
            text_color=self.colors["text"]
        ).pack(pady=50)

    def show_reports(self):
        """Show the reports view"""
        self.clear_main_content()
        ctk.CTkLabel(
            self.main_content,
            text="Reports - Coming Soon",
            font=("Helvetica", 24),
            text_color=self.colors["text"]
        ).pack(pady=50)

    def show_settings(self):
        """Show the settings view"""
        # Vérifier le mot de passe avant d'accéder aux paramètres
        self.ask_password_then_execute(self._show_settings)
    
    def _show_settings(self):
        """Affiche la vue des paramètres après vérification du mot de passe"""
        self.clear_main_content()
        
        settings_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        settings_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            settings_frame,
            text="⚙️ Paramètres",
            font=("Helvetica", 24, "bold"),
            text_color="#3498DB"
        ).pack(pady=(0, 30), anchor="w")
        
        # Option pour changer le mot de passe
        password_frame = ctk.CTkFrame(settings_frame, fg_color="#34495E")
        password_frame.pack(fill="x", pady=10, padx=20)
        
        ctk.CTkLabel(
            password_frame,
            text="Mot de passe parental",
            font=("Helvetica", 16, "bold"),
            text_color="#ECF0F1"
        ).pack(pady=(10, 5), padx=20, anchor="w")
        
        ctk.CTkLabel(
            password_frame,
            text="Modifiez le mot de passe utilisé pour accéder aux paramètres de contrôle parental.",
            font=("Helvetica", 12),
            text_color="#ECF0F1"
        ).pack(pady=(0, 10), padx=20, anchor="w")
        
        ctk.CTkButton(
            password_frame,
            text="Changer le mot de passe",
            command=self.change_password,
            fg_color="#3498DB",
            hover_color="#2980B9",
            font=("Helvetica", 14)
        ).pack(pady=(0, 20), padx=20)
        
        # À propos
        about_frame = ctk.CTkFrame(settings_frame, fg_color="#34495E")
        about_frame.pack(fill="x", pady=10, padx=20)
        
        ctk.CTkLabel(
            about_frame,
            text="À propos",
            font=("Helvetica", 16, "bold"),
            text_color="#ECF0F1"
        ).pack(pady=(10, 5), padx=20, anchor="w")
        
        ctk.CTkLabel(
            about_frame,
            text="Application de Contrôle Parental v1.0",
            font=("Helvetica", 12),
            text_color="#ECF0F1"
        ).pack(pady=(0, 5), padx=20, anchor="w")
        
        ctk.CTkLabel(
            about_frame,
            text="Cette application permet de contrôler l'accès aux logiciels sur cet ordinateur.",
            font=("Helvetica", 12),
            text_color="#ECF0F1"
        ).pack(pady=(0, 20), padx=20, anchor="w")

    def ask_password_then_execute(self, callback):
        """Demande le mot de passe puis exécute la fonction callback"""
        dialog = PasswordDialog(self, "Contrôle Parental", True, 
                              lambda pwd: self.verify_and_execute(pwd, callback))
    
    def verify_and_execute(self, password, callback):
        """Vérifie le mot de passe puis exécute la fonction callback"""
        if password is None:  # L'utilisateur a annulé
            return
            
        if self.password_manager.verify_password(password):
            # Mot de passe correct, exécuter le callback
            callback()
        else:
            # Mot de passe incorrect
            ctk.CTkLabel(
                self,
                text="❌ Mot de passe incorrect!",
                font=("Helvetica", 14),
                text_color="#E74C3C"
            ).place(relx=0.5, rely=0.1, anchor="center")
            # Faire disparaître le message après quelques secondes
            self.after(2000, lambda: [child.destroy() for child in self.winfo_children() 
                                    if isinstance(child, ctk.CTkLabel) and "❌" in child.cget("text")])

    def change_password(self):
        """Change le mot de passe parental"""
        dialog = PasswordDialog(self, "Changer le mot de passe", False, self.handle_password_change)
    
    def handle_password_change(self, password):
        """Gère le changement de mot de passe"""
        if password:
            self.password_manager.set_password(password)
            ctk.CTkLabel(
                self,
                text="✅ Mot de passe modifié avec succès!",
                font=("Helvetica", 14),
                text_color="#2ECC71"
            ).place(relx=0.5, rely=0.1, anchor="center")
            # Faire disparaître le message après quelques secondes
            self.after(3000, lambda: [child.destroy() for child in self.winfo_children() 
                                    if isinstance(child, ctk.CTkLabel) and "✅" in child.cget("text")])

if __name__ == "__main__":
    app = ParentalControlApp()
    app.mainloop()