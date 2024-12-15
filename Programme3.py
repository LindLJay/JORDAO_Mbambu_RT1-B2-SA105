import re
from datetime import datetime

def parse_ics_to_list(file_path):
    """
    Lit un fichier ICS et extrait les événements dans une liste de dictionnaires.
    """
    # Lire le contenu du fichier ICS
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Expression régulière pour capturer tous les blocs d'événements dans le fichier
    event_pattern = re.compile(r'BEGIN:VEVENT(.*?)END:VEVENT', re.DOTALL)
    events = event_pattern.findall(content)

    if not events:
        raise ValueError("Aucun événement trouvé dans le fichier ICS.")

    # Liste pour stocker les événements sous forme de dictionnaires
    events_list = []

    # Parcourir chaque événement extrait
    for event in events:
        # Dictionnaire pour stocker les données de l'événement
        event_data = {}

        # Expressions régulières pour extraire les données importantes
        patterns = {
            'UID': r'UID:(\S+)',
            'DTSTART': r'DTSTART:(\d{8}T\d{6}Z)',
            'DTEND': r'DTEND:(\d{8}T\d{6}Z)',
            'SUMMARY': r'SUMMARY:(.+)',
            'LOCATION': r'LOCATION:(.+)',
            'DESCRIPTION': r'DESCRIPTION:(.+)'
        }

        # Extraire les données de l'événement
        for key, pattern in patterns.items():
            match = re.search(pattern, event)
            if match:
                event_data[key] = match.group(1).strip()

        # Si DTSTART et DTEND sont présents, calculer la durée
        if 'DTSTART' in event_data and 'DTEND' in event_data:
            dtstart = datetime.strptime(event_data['DTSTART'], '%Y%m%dT%H%M%SZ')
            dtend = datetime.strptime(event_data['DTEND'], '%Y%m%dT%H%M%SZ')
            duration = dtend - dtstart
            hours, remainder = divmod(duration.seconds, 3600)
            minutes = remainder // 60
            event_data['DUREE'] = f"{hours:02}:{minutes:02}"
            event_data['DATE'] = dtstart.strftime('%d-%m-%Y')
            event_data['HEURE'] = dtstart.strftime('%H:%M')

        # Ajouter MODALITE à partir du premier mot de SUMMARY si disponible
        if 'SUMMARY' in event_data:
            event_data['MODALITE'] = event_data['SUMMARY'].split(' ')[0]

        # Ajouter l'événement au tableau des résultats
        events_list.append(event_data)

    return events_list

def filter_r107_sessions(events_list):
    """
    Filtre les séances de la ressource R1.07 (Informatique) associées à un TP.
    """
    filtered_sessions = []

    for event in events_list:
        # Vérifier si MODALITE est "R1.07" et le type d'activité est "TP"
        if 'MODALITE' in event and event['MODALITE'] == "R1.07":
            if 'SUMMARY' in event and "TP" in event['SUMMARY']:
                # Ajouter une ligne filtrée au tableau
                filtered_sessions.append({
                    'DATE': event.get('DATE', 'vide'),
                    'DUREE': event.get('DUREE', 'vide'),
                    'MODALITE': 'TP'
                })

    return filtered_sessions

# Exemple d'utilisation
file_path = 'ADE_RT1_Septembre2023_Decembre2023.ics'  # Fichier ICS d'entrée

try:
    # Étape 1 : Extraire les événements sous forme de liste
    all_events = parse_ics_to_list(file_path)

    # Étape 2 : Filtrer les événements R1.07 pour les TP
    r107_sessions = filter_r107_sessions(all_events)

    # Afficher les résultats
    if r107_sessions:
        print("Séances R1.07 filtrées :")
        for session in r107_sessions:
            print(session)
    else:
        print("Aucune séance R1.07 trouvée pour les TP.")

except Exception as e:
    print("Erreur :", e)
