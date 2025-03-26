import customtkinter as ctk
from tkinter import messagebox
from logic.block_logic import ProcessBlocker

class BlockGUI(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.blocker = ProcessBlocker()  # Instance de la classe ProcessBlocker

        # Configuration des widgets
        self.create_widgets()

    def create_widgets(self):
        # Titre
        title_label = ctk.CTkLabel(
            self,
            text="Bloquer Logiciel 🚫",
            font=("Helvetica", 24, "bold"),
            text_color="#ECF0F1"
        )
        title_label.pack(pady=20)

        # Widgets pour bloquer les logiciels
        process_frame = ctk.CTkFrame(self, fg_color="#34495E")
        process_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(
            process_frame,
            text="Nom du processus à bloquer :",
            font=("Arial", 14),
            text_color="#ECF0F1"
        ).pack(side="left", padx=10)

        self.process_entry = ctk.CTkEntry(process_frame, placeholder_text="Ex: notepad.exe", font=("Arial", 14))
        self.process_entry.pack(side="left", padx=10, fill="x", expand=True)

        add_button = ctk.CTkButton(
            process_frame,
            text="Ajouter ➕",
            command=self.add_blocked_process,
            font=("Arial", 12),
            fg_color="#3498DB",
            hover_color="#2980B9"
        )
        add_button.pack(side="right", padx=10)

        # Liste des processus bloqués
        blocked_list_frame = ctk.CTkFrame(self, fg_color="#34495E")
        blocked_list_frame.pack(pady=10, padx=20, fill="both", expand=True)

        ctk.CTkLabel(
            blocked_list_frame,
            text="Processus Bloqués :",
            font=("Arial", 16, "bold"),
            text_color="#ECF0F1"
        ).pack(pady=10)

        self.blocked_listbox = ctk.CTkTextbox(blocked_list_frame, height=100, state="disabled", font=("Arial", 14))
        self.blocked_listbox.pack(fill="both", expand=True)

        # Boutons de contrôle
        control_frame = ctk.CTkFrame(self, fg_color="transparent")
        control_frame.pack(pady=20)

        start_blocking_button = ctk.CTkButton(
            control_frame,
            text="Activer le Blocage 🔒",
            command=self.start_blocking,
            font=("Arial", 14),
            fg_color="#27AE60",
            hover_color="#229954"
        )
        start_blocking_button.pack(side="left", padx=10)

        stop_blocking_button = ctk.CTkButton(
            control_frame,
            text="Désactiver le Blocage 🔓",
            command=self.stop_blocking,
            font=("Arial", 14),
            fg_color="#E74C3C",
            hover_color="#C0392B"
        )
        stop_blocking_button.pack(side="left", padx=10)

    def add_blocked_process(self):
        """Ajoute un processus à la liste des processus bloqués."""
        process_name = self.process_entry.get().strip()
        if not process_name:
            messagebox.showwarning("Attention", "Veuillez saisir un nom de processus.")
            return

        self.blocker.add_blocked_process(process_name)
        self.process_entry.delete(0, "end")
        self.update_blocked_list()

    def update_blocked_list(self):
        """Met à jour l'affichage de la liste des processus bloqués."""
        self.blocked_listbox.configure(state="normal")
        self.blocked_listbox.delete("1.0", "end")
        self.blocked_listbox.insert("end", "\n".join(self.blocker.blocked_processes))
        self.blocked_listbox.configure(state="disabled")

    def start_blocking(self):
        """Démarre le blocage des processus."""
        self.blocker.start_blocking()
        messagebox.showinfo("Succès", "Blocage activé ! Les processus sélectionnés seront arrêtés.")

    def stop_blocking(self):
        """Arrête le blocage des processus."""
        self.blocker.stop_blocking()
        messagebox.showinfo("Succès", "Blocage désactivé ! Les processus ne seront plus arrêtés.")