import json
import os

# Chemin du fichier JSON pour stocker les tâches
TASKS_FILE = "tasks.json"

def load_tasks():
    """Charge les tâches depuis le fichier JSON."""
    if not os.path.exists(TASKS_FILE):
        # Initialise un fichier JSON vide s'il n'existe pas
        save_tasks({})
        return {}
    try:
        with open(TASKS_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        # Si le fichier JSON est corrompu, initialise un fichier vide
        save_tasks({})
        return {}

def save_tasks(tasks):
    """Enregistre les tâches dans le fichier JSON."""
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)
        
def update_task_in_date(date, task_index, new_task, new_start_time, new_end_time):
    """
    Modifie une tâche existante pour une date donnée.
    :param date: La date (format YYYY-MM-DD).
    :param task_index: L'index de la tâche à modifier.
    :param new_task: La nouvelle description de la tâche.
    :param new_start_time: La nouvelle heure de début (format HH:MM).
    :param new_end_time: La nouvelle heure de fin (format HH:MM).
    :return: True si la tâche est mise à jour, False sinon.
    """
    tasks = load_tasks()
    if date not in tasks or task_index < 0 or task_index >= len(tasks[date]):
        return False

    # Met à jour la tâche
    tasks[date][task_index] = {
        "task": new_task,
        "start_time": new_start_time,
        "end_time": new_end_time
    }
    save_tasks(tasks)
    return True

def add_task_to_date(date, task, start_time, end_time):
    """
    Ajoute une tâche avec une plage horaire pour une date donnée.
    :param date: La date (format YYYY-MM-DD).
    :param task: La description de la tâche.
    :param start_time: L'heure de début (format HH:MM).
    :param end_time: L'heure de fin (format HH:MM).
    :return: True si la tâche est ajoutée, False sinon.
    """
    tasks = load_tasks()
    if date not in tasks:
        tasks[date] = []
    
    # Validation : L'heure de début doit être avant l'heure de fin
    if start_time >= end_time:
        print("Erreur : L'heure de début doit être avant l'heure de fin.")
        return False

    # Ajoute la tâche avec sa plage horaire
    tasks[date].append({
        "task": task,
        "start_time": start_time,
        "end_time": end_time
    })
    save_tasks(tasks)
    return True

def get_tasks_for_date(date):
    """Récupère les tâches pour une date donnée."""
    tasks = load_tasks()
    if date not in tasks or not isinstance(tasks[date], list):
        return []  # Retourne une liste vide si les données sont invalides
    return tasks.get(date, [])

def delete_task_by_index(date, index):
    """Supprime une tâche pour une date donnée."""
    tasks = load_tasks()
    if date not in tasks or index < 0 or index >= len(tasks[date]):
        return False
    del tasks[date][index]
    save_tasks(tasks)
    return True

def update_task_in_date(date, task_index, new_task, new_start_time, new_end_time):
    """
    Met à jour une tâche existante pour une date donnée.
    :param date: La date (format YYYY-MM-DD).
    :param task_index: L'index de la tâche à modifier.
    :param new_task: La nouvelle description de la tâche.
    :param new_start_time: La nouvelle heure de début (format HH:MM).
    :param new_end_time: La nouvelle heure de fin (format HH:MM).
    :return: True si la tâche est mise à jour, False sinon.
    """
    tasks = load_tasks()
    if date not in tasks or task_index < 0 or task_index >= len(tasks[date]):
        return False

    # Met à jour la tâche
    tasks[date][task_index] = {
        "task": new_task,
        "start_time": new_start_time,
        "end_time": new_end_time
    }
    save_tasks(tasks)
    return True