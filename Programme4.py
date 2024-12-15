import selenium
from selenium.webdriver import firefox
import re
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt
from bokeh.plotting import figure, output_file, save
from bokeh.io.export import export_png

def parse_ics_to_list(file_path):
    """
    Lit un fichier ICS et extrait les événements dans une liste de dictionnaires.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    event_pattern = re.compile(r'BEGIN:VEVENT(.*?)END:VEVENT', re.DOTALL)
    events = event_pattern.findall(content)

    if not events:
        raise ValueError("Aucun événement trouvé dans le fichier ICS.")

    events_list = []

    for event in events:
        event_data = {}

        patterns = {
            'UID': r'UID:(\S+)',
            'DTSTART': r'DTSTART:(\d{8}T\d{6}Z)',
            'DTEND': r'DTEND:(\d{8}T\d{6}Z)',
            'SUMMARY': r'SUMMARY:(.+)',
            'LOCATION': r'LOCATION:(.+)',
            'DESCRIPTION': r'DESCRIPTION:(.+)'
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, event)
            if match:
                event_data[key] = match.group(1).strip()

        if 'DTSTART' in event_data:
            dtstart = datetime.strptime(event_data['DTSTART'], '%Y%m%dT%H%M%SZ')
            event_data['DATE'] = dtstart.strftime('%d-%m-%Y')
            event_data['MONTH'] = dtstart.strftime('%B')

        if 'SUMMARY' in event_data:
            event_data['MODALITE'] = event_data['SUMMARY'].split(' ')[0]

        events_list.append(event_data)

    return events_list

def filter_r107_sessions(events_list):
    """
    Filtre les séances de la ressource R1.07 (Informatique) associées à un TP.
    """
    filtered_sessions = []

    for event in events_list:
        if 'MODALITE' in event and event['MODALITE'] == "R1.07":
            if 'SUMMARY' in event and "TP" in event['SUMMARY']:
                filtered_sessions.append(event)

    return filtered_sessions

def generate_graph(data):
    """
    Génère un graphique du nombre de séances par mois et exporte en PNG.
    """
    # Compter le nombre de séances par mois
    month_counts = Counter([event['MONTH'] for event in data])

    # Préparer les données pour l'affichage
    months = ['September', 'October', 'November', 'December']
    counts = [month_counts.get(month, 0) for month in months]

    # Créer le graphique avec Bokeh
    output_file("r107_sessions.html")
    p = figure(title="Nombre de séances R1.07 TP par mois",
               x_range=months,
               height=350,  # Remplace plot_height par height
               toolbar_location=None,
               tools="")

    p.vbar(x=months, top=counts, width=0.9, color="navy")
    p.xgrid.grid_line_color = None
    p.y_range.start = 0

    # Exporter en PNG
    export_png(p, filename="r107_sessions.png")
    print("Graphique exporté sous r107_sessions.png")

# Exemple d'utilisation
file_path = 'ADE_RT1_Septembre2023_Decembre2023.ics'

try:
    all_events = parse_ics_to_list(file_path)
    r107_sessions = filter_r107_sessions(all_events)

    if r107_sessions:
        print("Nombre de séances R1.07 TP par mois :")
        generate_graph(r107_sessions)
    else:
        print("Aucune séance R1.07 trouvée pour les TP.")

except Exception as e:
    print("Erreur :", e)
