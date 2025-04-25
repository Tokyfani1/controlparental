import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import Calendar
from logic.todo_logic import add_task_to_date, get_tasks_for_date, delete_task_by_index,update_task_in_date

class CalendarApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Agenda avec Calendrier 📅")
        self.geometry("900x600")
        self.minsize(800, 500)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Palette de couleurs
        self.colors = {
            "background": "#2C3E50",
            "card": "#34495E",
            "accent": "#3498DB",
            "text": "#ECF0F1"
        }
        self.configure(fg_color=self.colors["background"])

        # Variables
        self.selected_date = None
        self.tasks = []

        # Widgets
        self.create_widgets()

    

    def create_widgets(self):
        """Crée les widgets de l'application."""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Colonne gauche : Calendrier
        left_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["card"])
        left_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.calendar = Calendar(left_frame, selectmode="day", font=("Arial", 12))
        self.calendar.pack(pady=10, padx=10, fill="both", expand=True)

        select_date_button = ctk.CTkButton(
            left_frame,
            text="Sélectionner la Date 📅",
            command=self.select_date,
            font=("Arial", 12),
            fg_color=self.colors["accent"],
            hover_color="#2980B9"
        )
        select_date_button.pack(pady=10, padx=10, fill="x")

        # Colonne droite : Gestion des tâches
        right_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        title_label = ctk.CTkLabel(
            right_frame,
            text="Tâches du Jour 📝",
            font=("Helvetica", 24, "bold"),
            text_color=self.colors["text"]
        )
        title_label.pack(pady=(0, 20))

        self.tasks_textbox = ctk.CTkTextbox(
            right_frame,
            height=250,
            width=500,
            state="disabled",
            font=("Arial", 14),
            text_color=self.colors["text"],
            fg_color=self.colors["background"]
        )
        self.tasks_textbox.pack(pady=10, padx=10, fill="both", expand=True)

        input_frame = ctk.CTkFrame(right_frame, fg_color=self.colors["card"])
        input_frame.pack(pady=10, fill="x")

        # Jour
        ctk.CTkLabel(input_frame, text="Jour:", font=("Arial", 12), text_color=self.colors["text"]).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.days_of_week = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        self.day_menu = ctk.CTkOptionMenu(input_frame, values=self.days_of_week, font=("Arial", 12))
        self.day_menu.grid(row=0, column=1, columnspan=2, padx=10, pady=5, sticky="we")

        # Heure de début
        ctk.CTkLabel(input_frame, text="Début:", font=("Arial", 12), text_color=self.colors["text"]).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.start_hour = ctk.CTkOptionMenu(input_frame, values=[f"{i:02}" for i in range(24)], font=("Arial", 12), width=80)
        self.start_hour.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.start_minute = ctk.CTkOptionMenu(input_frame, values=[f"{i:02}" for i in range(60)], font=("Arial", 12), width=80)
        self.start_minute.grid(row=1, column=2, padx=5, pady=5, sticky="w")

        # Heure de fin
        ctk.CTkLabel(input_frame, text="Fin:", font=("Arial", 12), text_color=self.colors["text"]).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.end_hour = ctk.CTkOptionMenu(input_frame, values=[f"{i:02}" for i in range(24)], font=("Arial", 12), width=80)
        self.end_hour.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.end_minute = ctk.CTkOptionMenu(input_frame, values=[f"{i:02}" for i in range(60)], font=("Arial", 12), width=80)
        self.end_minute.grid(row=2, column=2, padx=5, pady=5, sticky="w")

        # Champ de saisie pour la tâche
        self.task_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Ajouter une tâche...",
            font=("Arial", 12)
        )
        self.task_entry.grid(row=3, column=0, columnspan=3, padx=10, pady=5, sticky="we")

        # Bouton Ajouter Tâche
        self.add_task_button = ctk.CTkButton(
            input_frame,
            text="Ajouter ➕",
            command=self.add_task_with_time,
            font=("Arial", 12),
            fg_color=self.colors["accent"],
            hover_color="#2980B9"
        )
        self.add_task_button.grid(row=4, column=0, columnspan=3, padx=10, pady=5, sticky="we")

    def select_date(self):
        """Récupère la date sélectionnée dans le calendrier."""
        selected_date = self.calendar.get_date()
        if not selected_date:
            return
        self.selected_date = selected_date
        self.refresh_tasks()


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



    def reset_form(self):
        """Réinitialise le formulaire."""
        self.day_menu.set(self.days_of_week[0])  # Réinitialise le jour
        self.start_hour.set("00")               # Réinitialise l'heure de début
        self.start_minute.set("00")
        self.end_hour.set("00")                 # Réinitialise l'heure de fin
        self.end_minute.set("00")
        self.task_entry.delete(0, "end")        # Efface la description
        self.selected_task_index = None         # Réinitialise l'index sélectionné
        self.add_task_button.configure(text="Ajouter Activité ➕", command=self.add_task_with_time)





        
    def update_task(self):
        """Modifie une tâche existante."""
        if not self.selected_date:
            messagebox.showwarning("Attention", "Veuillez d'abord sélectionner une date.")
            return

        # Récupère les nouvelles valeurs du formulaire
        task = self.task_entry.get().strip()
        start_hour = self.start_hour.get()
        start_minute = self.start_minute.get()
        end_hour = self.end_hour.get()
        end_minute = self.end_minute.get()

        if not task:
            messagebox.showwarning("Attention", "Veuillez saisir une tâche.")
            return

        start_time = f"{start_hour}:{start_minute}"
        end_time = f"{end_hour}:{end_minute}"

        # Validation : L'heure de début doit être avant l'heure de fin
        if start_time >= end_time:
            messagebox.showerror("Erreur", "L'heure de début doit être avant l'heure de fin.")
            return

        # Met à jour la tâche via la logique métier
        if update_task_in_date(self.selected_date, self.selected_task_index, task, start_time, end_time):
            messagebox.showinfo("Succès", "Tâche modifiée avec succès ! ✏️")
        else:
            messagebox.showerror("Erreur", "Impossible de modifier la tâche.")

        # Réinitialise le formulaire et rafraîchit l'affichage
        self.reset_form()
        self.refresh_tasks()


    def select_task(self, index):
        """Sélectionne une tâche en cliquant dessus."""
        if index < 0 or index >= len(self.tasks):
            messagebox.showerror("Erreur", "Index invalide.")
            return

        selected_task = self.tasks[index]

        # Pré-remplit le formulaire avec les détails de la tâche sélectionnée
        self.task_entry.delete(0, "end")
        self.task_entry.insert(0, selected_task["task"])
        self.start_hour.set(selected_task["start_time"].split(":")[0])
        self.start_minute.set(selected_task["start_time"].split(":")[1])
        self.end_hour.set(selected_task["end_time"].split(":")[0])
        self.end_minute.set(selected_task["end_time"].split(":")[1])

        # Stocke l'index de la tâche sélectionnée
        self.selected_task_index = index

        # Change le texte du bouton "Ajouter ➕" en "Modifier ✏️"
        self.add_task_button.configure(text="Modifier Activité ✏️", command=self.update_task)
    def refresh_tasks(self):
        """Met à jour l'affichage des tâches pour la date sélectionnée."""
        if not self.selected_date:
            return

        # Efface le contenu précédent
        self.tasks_textbox.configure(state="normal")
        self.tasks_textbox.delete("1.0", "end")

        # Récupère les tâches pour la date sélectionnée
        self.tasks = get_tasks_for_date(self.selected_date)

        if not self.tasks:
            self.tasks_textbox.insert("end", "Aucune tâche pour cette date. 📅\n")
        else:
            for idx, task in enumerate(self.tasks, start=1):
                # Affiche la tâche dans la zone de texte
                task_text = f"{idx}. 📌 {task['start_time']} - {task['end_time']} | {task['task']}\n"
                self.tasks_textbox.insert("end", task_text)

                # Ajoute un tag pour rendre chaque tâche cliquable
                tag_name = f"task_{idx}"
                self.tasks_textbox.tag_add(tag_name, f"{idx}.0", f"{idx}.end")
                self.tasks_textbox.tag_config(
                    tag_name,
                    foreground="white",
                    underline=True
                )
                self.tasks_textbox.tag_bind(
                    tag_name,
                    "<Button-1>",
                    lambda event, idx=idx - 1: self.select_task(idx)
                )

        self.tasks_textbox.configure(state="disabled")

    def add_task_with_time(self):
        """Ajoute une nouvelle tâche avec une plage horaire."""
        if not self.selected_date:
            messagebox.showwarning("Attention", "Veuillez d'abord sélectionner une date.")
            return

        task = self.task_entry.get().strip()
        if not task:
            messagebox.showwarning("Attention", "Veuillez saisir une tâche.")
            return

        # Récupère les heures de début et de fin
        start_hour = self.start_hour.get()
        start_minute = self.start_minute.get()
        end_hour = self.end_hour.get()
        end_minute = self.end_minute.get()

        start_time = f"{start_hour}:{start_minute}"
        end_time = f"{end_hour}:{end_minute}"

        # Validation : L'heure de début doit être avant l'heure de fin
        if start_time >= end_time:
            messagebox.showerror("Erreur", "L'heure de début doit être avant l'heure de fin.")
            return

        # Ajoute la tâche via la logique métier
        if add_task_to_date(self.selected_date, task, start_time, end_time):
            messagebox.showinfo("Succès", "Tâche ajoutée avec succès ! ✅")
        else:
            messagebox.showerror("Erreur", "Impossible d'ajouter la tâche.")

        # Réinitialise le champ de saisie et met à jour l'affichage
        self.task_entry.delete(0, "end")
        self.refresh_tasks()


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
        
        # Réinitialise le formulaire après chaque action
        self.reset_form()
        self.refresh_all_activities()