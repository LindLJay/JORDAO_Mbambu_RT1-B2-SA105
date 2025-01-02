import re
from datetime import datetime
import matplotlib.pyplot as plt
from icalendar import Calendar
import markdown

# Programme 3 : Extraction et filtrage des données
def parse_ics_to_list(file_path):
    """
    Lit un fichier ICS et extrait les événements dans une liste de dictionnaires.

    Args:
        file_path (str): Chemin vers le fichier ICS.

    Returns:
        list: Liste de dictionnaires contenant les données des événements.
    """
    # Ouvre et lit le contenu du fichier ICS
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Utilise une expression régulière pour extraire les blocs d'événements (entre BEGIN:VEVENT et END:VEVENT)
    event_pattern = re.compile(r'BEGIN:VEVENT(.*?)END:VEVENT', re.DOTALL)
    events = event_pattern.findall(content)

    # Si aucun événement n'est trouvé, lever une exception
    if not events:
        raise ValueError("Aucun événement trouvé dans le fichier ICS.")

    # Liste pour stocker les événements extraits sous forme de dictionnaires
    events_list = []

    # Parcourt chaque événement extrait
    for event in events:
        event_data = {}  # Dictionnaire pour contenir les données de l'événement

        # Définit les modèles regex pour extraire les champs importants
        patterns = {
            'UID': r'UID:(\S+)',
            'DTSTART': r'DTSTART:(\d{8}T\d{6}Z)',
            'DTEND': r'DTEND:(\d{8}T\d{6}Z)',
            'SUMMARY': r'SUMMARY:(.+)',
            'LOCATION': r'LOCATION:(.+)',
            'DESCRIPTION': r'DESCRIPTION:(.+)'
        }

        # Cherche chaque champ défini dans l'événement et les ajoute au dictionnaire
        for key, pattern in patterns.items():
            match = re.search(pattern, event)
            if match:
                event_data[key] = match.group(1).strip()

        # Calcule la durée de l'événement si DTSTART et DTEND sont disponibles
        if 'DTSTART' in event_data and 'DTEND' in event_data:
            dtstart = datetime.strptime(event_data['DTSTART'], '%Y%m%dT%H%M%SZ')
            dtend = datetime.strptime(event_data['DTEND'], '%Y%m%dT%H%M%SZ')
            duration = dtend - dtstart
            hours, remainder = divmod(duration.seconds, 3600)
            minutes = remainder // 60
            event_data['DUREE'] = f"{hours:02}:{minutes:02}"
            event_data['DATE'] = dtstart.strftime('%d-%m-%Y')
            event_data['HEURE'] = dtstart.strftime('%H:%M')

        # Ajoute MODALITE à partir du premier mot de SUMMARY si ce champ est présent
        if 'SUMMARY' in event_data:
            event_data['MODALITE'] = event_data['SUMMARY'].split(' ')[0]

        # Ajoute l'événement à la liste finale
        events_list.append(event_data)

    return events_list


def filter_r107_sessions(events_list):
    """
    Filtre les événements correspondant aux séances de la ressource R1.07 et au type TP.

    Args:
        events_list (list): Liste de dictionnaires contenant les événements.

    Returns:
        list: Liste filtrée contenant les séances R1.07 de type TP.
    """
    filtered_sessions = []

    # Parcourt tous les événements pour vérifier les critères de filtre
    for event in events_list:
        if 'MODALITE' in event and event['MODALITE'] == "R1.07":
            if 'SUMMARY' in event and "TP" in event['SUMMARY']:
                # Ajoute uniquement les événements correspondant aux critères
                filtered_sessions.append({
                    'DATE': event.get('DATE', 'vide'),
                    'DUREE': event.get('DUREE', 'vide'),
                    'MODALITE': 'TP'
                })

    return filtered_sessions


# Programme 4 : Création du diagramme
def generate_chart(file_path):
    """
    Génère un diagramme des séances de TP par mois à partir du fichier ICS.

    Args:
        file_path (str): Chemin vers le fichier ICS.

    Returns:
        str: Chemin vers le fichier PNG contenant le diagramme.
    """
    # Lecture du fichier ICS et parsing avec icalendar
    with open(file_path, 'r') as f:
        calendar = Calendar.from_ical(f.read())

    # Liste des mois et dictionnaire pour compter les séances
    months = ['Septembre', 'Octobre', 'Novembre', 'Décembre']
    session_counts = {month: 0 for month in months}

    # Traduction des noms de mois anglais vers le français
    month_translation = {
        'September': 'Septembre',
        'October': 'Octobre',
        'November': 'Novembre',
        'December': 'Décembre'
    }

    # Parcourt tous les événements pour compter les séances
    for event in calendar.walk('VEVENT'):
        summary = event.get('SUMMARY')
        dtstart = event.get('DTSTART').dt

        # Vérifie si l'événement est une séance de TP
        if 'TP' in summary:
            month_name = dtstart.strftime('%B')
            month_name = month_translation.get(month_name, month_name)
            if month_name in session_counts:
                session_counts[month_name] += 1

    # Prépare les données pour le graphique
    x_labels = list(session_counts.keys())
    y_values = list(session_counts.values())

    # Crée le diagramme
    plt.figure(figsize=(10, 6))
    plt.bar(x_labels, y_values, color='skyblue')
    plt.title('Nombre de séances de TP (Septembre-Décembre 2023)', fontsize=14)
    plt.xlabel('Mois', fontsize=12)
    plt.ylabel('Nombre de séances', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Sauvegarde le graphique dans un fichier PNG
    output_file = 'seances_tp.png'
    plt.savefig(output_file)
    plt.close()

    return output_file


# Génération du fichier Markdown et HTML
def generate_markdown_html(file_path, sessions, chart_path):
    """
    Génère un fichier HTML contenant un tableau et un diagramme des séances.

    Args:
        file_path (str): Chemin vers le fichier ICS.
        sessions (list): Liste des séances à inclure dans le tableau.
        chart_path (str): Chemin vers le fichier PNG du diagramme.
    """
    # Contenu Markdown
    markdown_content = "# Mes travaux précédents\n\n"
    markdown_content += "## Tableau des séances de R1.07\n\n"
    markdown_content += "| Date       | Durée | Modalité |\n"
    markdown_content += "|------------|-------|----------|\n"
    for session in sessions:
        markdown_content += f"| {session['DATE']} | {session['DUREE']} | {session['MODALITE']} |\n"

    markdown_content += "\n## Diagramme des séances de TP\n\n"
    markdown_content += f"![Diagramme des TP]({chart_path})\n\n"

    # Conversion en HTML
    html_content = markdown.markdown(markdown_content, extensions=['tables'])

    # Écriture dans un fichier HTML
    with open("travaux_precedents.html", "w", encoding="utf-8") as file:
        file.write(html_content)

    print("Fichier HTML généré : travaux_precedents.html")


# Chemin du fichier ICS
file_path = 'ADE_RT1_Septembre2023_Decembre2023.ics'

try:
    # Étape 1 : Extraction des événements
    all_events = parse_ics_to_list(file_path)

    # Étape 2 : Filtrage des séances R1.07
    r107_sessions = filter_r107_sessions(all_events)

    # Étape 3 : Génération du diagramme
    chart_path = generate_chart(file_path)

    # Étape 4 : Création du fichier HTML
    generate_markdown_html(file_path, r107_sessions, chart_path)

except Exception as e:
    print("Erreur :", e)

