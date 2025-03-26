import json
from datetime import datetime

# Chemin vers le fichier JSON
SCHEDULE_FILE = "schedule.json"

def load_schedule():
    """
    Charge la liste des activités depuis le fichier JSON.
    Si le fichier n'existe pas ou est corrompu, retourne une liste vide.
    """
    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        # Si le fichier n'existe pas, retourne une liste vide
        return []
    except json.JSONDecodeError:
        # Si le fichier est corrompu, retourne une liste vide
        return []

def save_schedule(schedule):
    """
    Sauvegarde la liste des activités dans le fichier JSON.
    """
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as file:
        json.dump(schedule, file, indent=4, ensure_ascii=False)

def add_activity(day, start_time, end_time, activity):
    """
    Ajoute une nouvelle activité à l'emploi du temps après validation des conflits.
    :param day: Jour de l'activité.
    :param start_time: Heure de début (format HH:MM).
    :param end_time: Heure de fin (format HH:MM).
    :param activity: Description de l'activité.
    :return: True si l'ajout réussit, False sinon.
    """
    if check_time_overlap(day, start_time, end_time):
        print("Erreur : Une activité existe déjà pour cette plage horaire.")
        return False

    schedule = load_schedule()
    new_activity = {
        "day": day,
        "start_time": start_time,
        "end_time": end_time,
        "activity": activity
    }
    schedule.append(new_activity)
    save_schedule(schedule)
    return True

def update_activity(index, new_day, new_start_time, new_end_time, new_activity):
    """
    Met à jour une activité spécifique après validation des conflits.
    :param index: Index de l'activité à modifier (0-based).
    :param new_day: Nouveau jour.
    :param new_start_time: Nouvelle heure de début.
    :param new_end_time: Nouvelle heure de fin.
    :param new_activity: Nouvelle description de l'activité.
    :return: True si la mise à jour réussit, False sinon.
    """
    schedule = load_schedule()
    if 0 <= index < len(schedule):  # Vérifie si l'index est valide
        # Vérifie les conflits, mais ignore l'activité actuelle
        for i, activity in enumerate(schedule):
            if i != index and activity["day"] == new_day:
                existing_start = datetime.strptime(activity["start_time"], "%H:%M")
                existing_end = datetime.strptime(activity["end_time"], "%H:%M")
                new_start = datetime.strptime(new_start_time, "%H:%M")
                new_end = datetime.strptime(new_end_time, "%H:%M")

                if not (new_end <= existing_start or new_start >= existing_end):
                    print("Erreur : Une activité existe déjà pour cette plage horaire.")
                    return False

        # Aucun conflit détecté, mise à jour de l'activité
        schedule[index] = {
            "day": new_day,
            "start_time": new_start_time,
            "end_time": new_end_time,
            "activity": new_activity
        }
        save_schedule(schedule)
        return True
    return False

def check_time_overlap(day, start_time, end_time):
    """
    Vérifie s'il y a un chevauchement d'horaire pour une nouvelle activité.
    :param day: Jour de l'activité.
    :param start_time: Heure de début (format HH:MM).
    :param end_time: Heure de fin (format HH:MM).
    :return: True si un chevauchement existe, False sinon.
    """
    schedule = load_schedule()
    for activity in schedule:
        if activity["day"] == day:
            existing_start = datetime.strptime(activity["start_time"], "%H:%M")
            existing_end = datetime.strptime(activity["end_time"], "%H:%M")
            new_start = datetime.strptime(start_time, "%H:%M")
            new_end = datetime.strptime(end_time, "%H:%M")

            # Vérifie si les plages horaires se chevauchent
            if not (new_end <= existing_start or new_start >= existing_end):
                return True  # Conflit détecté
    return False  # Pas de conflit


def list_activities(day=None):
    """
    Liste toutes les activités, éventuellement filtrées par jour.
    :param day: Jour spécifique (facultatif). Si None, retourne toutes les activités.
    :return: Liste des activités.
    """
    schedule = load_schedule()
    if day:
        return [activity for activity in schedule if activity["day"] == day]
    return schedule

def delete_all_activities():
    """
    Supprime toutes les activités de l'emploi du temps.
    """
    save_schedule([])

def delete_activity_by_index(index):
    """
    Supprime une activité spécifique en fonction de son index.
    :param index: Index de l'activité à supprimer (0-based).
    :return: True si la suppression réussit, False sinon.
    """
    schedule = load_schedule()
    if 0 <= index < len(schedule):  # Vérifie si l'index est valide
        del schedule[index]
        save_schedule(schedule)
        return True
    return False

def validate_time(time_str):
    """
    Valide une chaîne de caractères représentant une heure au format HH:MM.
    :param time_str: Chaîne de caractères au format HH:MM.
    :return: True si l'heure est valide, False sinon.
    """
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False



