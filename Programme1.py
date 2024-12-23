import re

def parse_ics_to_csv(file_path):
    """
    Lis un fichier ICS contenant un événement et le convertit en pseudo-CSV.
    """

    # Lire le fichier ICS et charger son contenu dans une variable
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Définir une expression régulière pour capturer un bloc d'événement unique
    # Les événements sont délimités par les balises BEGIN:VEVENT et END:VEVENT
    event_pattern = re.compile(r'BEGIN:VEVENT(.*?)END:VEVENT', re.DOTALL)
    event_match = event_pattern.search(content)

    # Vérifier si un événement est trouvé dans le fichier
    if not event_match:
        # Si aucun événement n'est trouvé, lever une exception
        raise ValueError("Aucun événement trouvé dans le fichier ICS.")

    # Extraire le contenu de l'événement
    event = event_match.group(1)

    # Initialiser un dictionnaire pour stocker les données extraites
    csv_data = {
        'UID': None,          # Identifiant unique de l'événement
        'DTSTART': None,      # Date et heure de début
        'DUREE': None,        # Durée de l'événement (calculée à partir de DTSTART et DTEND)
        'MODALITE': None,     # Modalité (dérivé du champ SUMMARY)
        'SUMMARY': None,      # Résumé ou description courte de l'événement
        'LOCATION': None,     # Lieu où l'événement se déroule
    }

    # Définir des expressions régulières pour extraire des champs spécifiques
    patterns = {
        'UID': r'UID:(\S+)',                       # Identifiant unique
        'DTSTART': r'DTSTART:(\d{8}T\d{6}Z)',     # Date et heure de début au format UTC
        'DTEND': r'DTEND:(\d{8}T\d{6}Z)',         # Date et heure de fin au format UTC
        'SUMMARY': r'SUMMARY:(.+)',               # Résumé de l'événement
        'LOCATION': r'LOCATION:(.+)',             # Lieu de l'événement
        'DESCRIPTION': r'DESCRIPTION:(.+)'        # Description détaillée (souvent multiligne)
    }

    # Dictionnaire temporaire pour stocker les données extraites
    extracted_data = {}
    for key, pattern in patterns.items():
        # Rechercher chaque champ dans le bloc d'événement
        match = re.search(pattern, event)
        if match:
            # Si une correspondance est trouvée, la nettoyer et la stocker
            extracted_data[key] = match.group(1).strip()

    # Calculer la durée (DTEND - DTSTART)
    if 'DTSTART' in extracted_data and 'DTEND' in extracted_data:
        from datetime import datetime

        # Convertir DTSTART et DTEND en objets datetime pour les manipuler
        dtstart = datetime.strptime(extracted_data['DTSTART'], '%Y%m%dT%H%M%SZ')
        dtend = datetime.strptime(extracted_data['DTEND'], '%Y%m%dT%H%M%SZ')
        duration = dtend - dtstart

        # Calculer la durée en heures et minutes
        hours, remainder = divmod(duration.seconds, 3600)
        minutes = remainder // 60
        csv_data['DUREE'] = f"{hours:02}:{minutes:02}"  # Formater la durée au format HH:MM

    # Mapper les données extraites aux champs pseudo-CSV
    csv_data['UID'] = extracted_data.get('UID', '')  # Identifiant unique de l'événement

    if 'DTSTART' in extracted_data:
        # Convertir DTSTART en date et heure lisibles
        dtstart = datetime.strptime(extracted_data['DTSTART'], '%Y%m%dT%H%M%SZ')
        csv_data['DATE'] = dtstart.strftime('%d-%m-%Y')  # Date au format JJ-MM-AAAA
        csv_data['HEURE'] = dtstart.strftime('%H:%M')   # Heure au format HH:MM

    # Supposons que la modalité est le premier mot de SUMMARY
    csv_data['MODALITE'] = extracted_data.get('SUMMARY', '').split(' ')[0]  # Modalité (ex. "Cours", "TD", etc.)
    csv_data['SUMMARY'] = extracted_data.get('SUMMARY', '')  # Résumé complet
    csv_data['LOCATION'] = extracted_data.get('LOCATION', '')  # Lieu de l'événement

    # Extraire les informations sur les professeurs et groupes à partir de DESCRIPTION
    description = extracted_data.get('DESCRIPTION', '')
    description_parts = description.split('\n')  # Diviser la description en lignes

    # Construire la ligne pseudo-CSV
    # Chaque champ est séparé par un point-virgule
    csv_line = (
        f"{csv_data['UID']};{csv_data['DATE']};{csv_data['HEURE']};{csv_data['DUREE']};"
        f"{csv_data['MODALITE']};{csv_data['SUMMARY']};{csv_data['LOCATION']};"
    )

    return csv_line  # Retourner la chaîne formatée au format pseudo-CSV

# Exemple d'utilisation
file_path = 'evenementSAE_15GroupeA1.ics'  # Remplacez par le chemin de votre fichier ICS
try:
    # Tenter de convertir l'événement en pseudo-CSV
    pseudo_csv = parse_ics_to_csv(file_path)
    print("Pseudo-CSV:", pseudo_csv)
except Exception as e:
    # Gérer les erreurs et afficher un message approprié
    print("Erreur:", e)
