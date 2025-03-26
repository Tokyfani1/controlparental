import customtkinter as ctk
from tkinter import messagebox
from todo_logic import add_activity, list_activities, delete_all_activities, delete_activity_by_index, update_activity

class TodoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuration de la fenêtre
        self.title("Mon Emploi du Temps")
        self.geometry("900x700")
        self.minsize(800, 600)

        # Thème et couleurs
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Variables
        self.days_of_week = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        self.current_day = None
        self.selected_activity_index = None  # Stocke l'index de l'activité sélectionnée

        # Palette de couleurs
        self.colors = {
            "background": "#2C3E50",
            "card": "#34495E",
            "accent": "#3498DB",
            "text": "#ECF0F1"
        }

        # Configure la fenêtre
        self.configure(fg_color=self.colors["background"])

        # Widgets
        self.create_widgets()

    def create_widgets(self):
        # Conteneur principal déroulant
        scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scrollable_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Titre
        title_label = ctk.CTkLabel(
            scrollable_frame,
            text="Mon Emploi du Temps 📅",
            font=("Helvetica", 28, "bold"),
            text_color=self.colors["text"]
        )
        title_label.pack(pady=(0, 20), fill="x")

        # Barre de boutons pour filtrer par jour
        day_frame = ctk.CTkFrame(scrollable_frame, fg_color=self.colors["card"])
        day_frame.pack(pady=10, fill="x")

        for day in self.days_of_week:
            button = ctk.CTkButton(
                day_frame,
                text=day,
                command=lambda d=day: self.show_tasks_for_day(d),
                width=100,
                height=40,
                font=("Arial", 12),
                fg_color=self.colors["accent"],
                hover_color="#2980B9"
            )
            button.pack(side="left", padx=5, pady=10, expand=True)

        # Formulaire pour ajouter/modifier une activité
        input_frame = ctk.CTkFrame(scrollable_frame, fg_color=self.colors["card"])
        input_frame.pack(pady=10, fill="x")

        # Jour
        ctk.CTkLabel(input_frame, text="Jour:", font=("Arial", 14), text_color=self.colors["text"]).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.day_menu = ctk.CTkOptionMenu(input_frame, values=self.days_of_week, font=("Arial", 12))
        self.day_menu.grid(row=0, column=1, columnspan=2, padx=10, pady=5, sticky="we")

        # Heure de début
        ctk.CTkLabel(input_frame, text="Début:", font=("Arial", 14), text_color=self.colors["text"]).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.start_hour = ctk.CTkOptionMenu(input_frame, values=[f"{i:02}" for i in range(24)], font=("Arial", 12), width=80)
        self.start_hour.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.start_minute = ctk.CTkOptionMenu(input_frame, values=[f"{i:02}" for i in range(60)], font=("Arial", 12), width=80)
        self.start_minute.grid(row=1, column=2, padx=5, pady=5, sticky="w")

        # Heure de fin
        ctk.CTkLabel(input_frame, text="Fin:", font=("Arial", 14), text_color=self.colors["text"]).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.end_hour = ctk.CTkOptionMenu(input_frame, values=[f"{i:02}" for i in range(24)], font=("Arial", 12), width=80)
        self.end_hour.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.end_minute = ctk.CTkOptionMenu(input_frame, values=[f"{i:02}" for i in range(60)], font=("Arial", 12), width=80)
        self.end_minute.grid(row=2, column=2, padx=5, pady=5, sticky="w")

        # Activité
        ctk.CTkLabel(input_frame, text="Activité:", font=("Arial", 14), text_color=self.colors["text"]).grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.activity_entry = ctk.CTkEntry(input_frame, placeholder_text="Ex: Devoirs, Sport...", font=("Arial", 12))
        self.activity_entry.grid(row=3, column=1, columnspan=2, padx=10, pady=5, sticky="we")

        # Bouton pour ajouter ou modifier une activité
        self.add_button = ctk.CTkButton(
            input_frame,
            text="Ajouter Activité ➕",
            command=self.add_or_update_activity_gui,
            font=("Arial", 12),
            fg_color=self.colors["accent"],
            hover_color="#2980B9"
        )
        self.add_button.grid(row=4, column=0, columnspan=3, pady=10, padx=10, sticky="we")

        # Zone d'affichage des activités avec barre de défilement
        display_frame = ctk.CTkFrame(scrollable_frame, fg_color=self.colors["card"])
        display_frame.pack(pady=10, fill="both", expand=True)

        # Barre de défilement verticale
        scrollbar = ctk.CTkScrollbar(display_frame, orientation="vertical")
        scrollbar.pack(side="right", fill="y")

        # Zone de texte pour afficher les activités
        self.activities_textbox = ctk.CTkTextbox(
            display_frame,
            height=250,
            width=800,
            state="disabled",
            font=("Arial", 14),
            text_color=self.colors["text"],
            fg_color=self.colors["background"],
            yscrollcommand=scrollbar.set
        )
        self.activities_textbox.pack(pady=10, padx=10, fill="both", expand=True)

        # Configure la barre de défilement pour contrôler la zone de texte
        scrollbar.configure(command=self.activities_textbox.yview)

        # Cadre pour les boutons (button_frame)
        button_frame = ctk.CTkFrame(display_frame, fg_color="transparent")
        button_frame.pack(pady=10)

        # Bouton Rafraîchir
        refresh_button = ctk.CTkButton(
            button_frame,
            text="Toutes les Activités 🔄",
            command=self.refresh_all_activities,
            font=("Arial", 12),
            fg_color=self.colors["accent"],
            hover_color="#2980B9",
            width=150
        )
        refresh_button.pack(side="left", padx=10)

        # Bouton Effacer Tout
        clear_button = ctk.CTkButton(
            button_frame,
            text="Effacer Tout ❌",
            command=self.clear_all_activities,
            font=("Arial", 12),
            fg_color="#E74C3C",
            hover_color="#C0392B",
            width=150
        )
        clear_button.pack(side="left", padx=10)

        # Bouton Supprimer Activité
        delete_button = ctk.CTkButton(
            button_frame,
            text="Supprimer Activité 🗑️",
            command=self.delete_selected_activity_click,
            font=("Arial", 12),
            fg_color="#E74C3C",
            hover_color="#C0392B",
            width=150
        )
        delete_button.pack(side="left", padx=10)

        # Bouton Modifier Activité
        edit_button = ctk.CTkButton(
            button_frame,
            text="Modifier Activité ✏️",
            command=self.edit_selected_activity,
            font=("Arial", 12),
            fg_color="#27AE60",
            hover_color="#229954",
            width=150
        )
        edit_button.pack(side="left", padx=10)

        # Initialisation de la liste des activités
        self.refresh_all_activities()

    def refresh_all_activities(self):
        """Affiche toutes les activités (pas de filtre)."""
        self.current_day = None
        self.refresh_activities()



    def refresh_activities(self, day=None):
        """Met à jour l'affichage des activités en fonction du jour sélectionné."""
        # Efface tout le contenu précédent
        self.activities_textbox.configure(state="normal")
        self.activities_textbox.delete("1.0", "end")

        # Charge la liste des activités
        activities = list_activities(day) if day else list_activities()

        if not activities:
            self.activities_textbox.insert("end", "Aucune activité planifiée. 📅\n")
        else:
            for idx, activity in enumerate(activities, start=1):
                activity_text = f"{idx}. 📌 {activity['day']} | {activity['start_time']} - {activity['end_time']} | {activity['activity']}\n"
                self.activities_textbox.insert("end", activity_text)

                # Ajoute un tag pour rendre chaque activité cliquable
                tag_name = f"activity_{idx}"
                self.activities_textbox.tag_add(tag_name, f"{idx}.0", f"{idx}.end")
                self.activities_textbox.tag_config(
                    tag_name,
                    foreground="white",  # Couleur blanche pour une meilleure lisibilité
                    underline=True  # Souligne le texte pour indiquer qu'il est cliquable
                )
                self.activities_textbox.tag_bind(
                    tag_name,
                    "<Button-1>",
                    lambda event, idx=idx - 1: self.select_activity(idx)
                )

        # Désactive le widget après modifications
        self.activities_textbox.configure(state="disabled")





    def select_activity(self, index):
        """Sélectionne une activité en cliquant dessus."""
        self.selected_activity_index = index
        activities = list_activities()
        selected_activity = activities[index]

        # Pré-remplit le formulaire avec les détails de l'activité sélectionnée
        self.day_menu.set(selected_activity["day"])
        self.start_hour.set(selected_activity["start_time"].split(":")[0])
        self.start_minute.set(selected_activity["start_time"].split(":")[1])
        self.end_hour.set(selected_activity["end_time"].split(":")[0])
        self.end_minute.set(selected_activity["end_time"].split(":")[1])
        self.activity_entry.delete(0, "end")
        self.activity_entry.insert(0, selected_activity["activity"])

        # Change le texte du bouton "Ajouter Activité" en "Modifier Activité"
        self.add_button.configure(text="Modifier Activité ✏️")



    def add_or_update_activity_gui(self):
        """Ajoute ou modifie une activité via l'interface graphique."""
        day = self.day_menu.get()
        start_hour = self.start_hour.get()
        start_minute = self.start_minute.get()
        end_hour = self.end_hour.get()
        end_minute = self.end_minute.get()
        activity = self.activity_entry.get().strip()

        if not activity:
            messagebox.showwarning("Attention", "Veuillez saisir une activité.")
            return

        start_time_str = f"{start_hour}:{start_minute}"
        end_time_str = f"{end_hour}:{end_minute}"

        if start_time_str >= end_time_str:
            messagebox.showerror("Erreur", "L'heure de début doit être avant l'heure de fin.")
            return

        # Vérifie les conflits d'horaire
        if self.selected_activity_index is not None:
            # Modification de l'activité sélectionnée
            if not update_activity(
                self.selected_activity_index,
                day,
                start_time_str,
                end_time_str,
                activity
            ):
                messagebox.showerror("Erreur", "Une activité existe déjà pour cette plage horaire.")
                return
            messagebox.showinfo("Succès", "Activité modifiée avec succès ! ✏️")
        else:
            # Ajout d'une nouvelle activité
            if not add_activity(day, start_time_str, end_time_str, activity):
                messagebox.showerror("Erreur", "Une activité existe déjà pour cette plage horaire.")
                return
            messagebox.showinfo("Succès", "Activité ajoutée avec succès ! 🎉")

        self.reset_form()
        self.refresh_all_activities()

    def reset_form(self):
        """Réinitialise le formulaire."""
        self.day_menu.set(self.days_of_week[0])
        self.start_hour.set("00")
        self.start_minute.set("00")
        self.end_hour.set("00")
        self.end_minute.set("00")
        self.activity_entry.delete(0, "end")
        self.selected_activity_index = None
        self.add_button.configure(text="Ajouter Activité ➕")

    def edit_selected_activity(self):
        """Modifie l'activité sélectionnée."""
        if self.selected_activity_index is None:
            messagebox.showerror("Erreur", "Aucune activité sélectionnée. Veuillez cliquer sur une activité pour la modifier.")
            return

        # Appelle directement la méthode pour pré-remplir le formulaire
        activities = list_activities()
        selected_activity = activities[self.selected_activity_index]
        self.day_menu.set(selected_activity["day"])
        self.start_hour.set(selected_activity["start_time"].split(":")[0])
        self.start_minute.set(selected_activity["start_time"].split(":")[1])
        self.end_hour.set(selected_activity["end_time"].split(":")[0])
        self.end_minute.set(selected_activity["end_time"].split(":")[1])
        self.activity_entry.delete(0, "end")
        self.activity_entry.insert(0, selected_activity["activity"])

        # Change le texte du bouton "Ajouter Activité" en "Modifier Activité"
        self.add_button.configure(text="Modifier Activité ✏️")

    def delete_selected_activity_click(self):
        """Supprime l'activité sélectionnée via le bouton 'Supprimer Activité 🗑️'."""
        if self.selected_activity_index is None:
            messagebox.showerror("Erreur", "Aucune activité sélectionnée. Veuillez cliquer sur une activité pour la sélectionner.")
            return

        if delete_activity_by_index(self.selected_activity_index):
            messagebox.showinfo("Succès", f"L'activité {self.selected_activity_index + 1} a été supprimée.")
            self.reset_form()
            self.refresh_all_activities()
        else:
            messagebox.showerror("Erreur", "Index invalide. Veuillez réessayer.")

    def show_tasks_for_day(self, day):
        """Affiche les tâches pour un jour spécifique."""
        self.current_day = day
        self.refresh_activities(day)

    def clear_all_activities(self):
        """Supprime toutes les activités après confirmation."""
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer toutes les activités ?"):
            delete_all_activities()
            self.refresh_all_activities()
            messagebox.showinfo("Succès", "Toutes les activités ont été supprimées.")