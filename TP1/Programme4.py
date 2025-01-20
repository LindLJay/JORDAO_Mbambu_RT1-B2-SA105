import matplotlib.pyplot as plt
import datetime
from icalendar import Calendar

# Chargement du fichier ICS
# Chemin du fichier ICS contenant les événements. Vous pourriez rendre ce chemin configurable.
file_path = 'ADE_RT1_Septembre2023_Decembre2023.ics'
with open(file_path, 'r') as f:
    # Lecture et parsing du fichier ICS
    calendar = Calendar.from_ical(f.read())

# Extraction des événements pour identifier les séances de TP
# Liste des mois concernés par l'analyse
months = ['Septembre', 'Octobre', 'Novembre', 'Décembre']
# Initialisation d'un dictionnaire pour compter les séances par mois
session_counts = {month: 0 for month in months}

# Traduction des noms de mois de l'anglais au français
month_translation = {
    'September': 'Septembre',
    'October': 'Octobre',
    'November': 'Novembre',
    'December': 'Décembre'
}

# Inspection et comptage des événements
for event in calendar.walk('VEVENT'):
    summary = event.get('SUMMARY')
    dtstart = event.get('DTSTART').dt

    # Vérifier que c'est une séance de TP
    if 'TP' in summary:  # Remplacer "A1" par des critères adaptés si nécessaire
        # Récupération et traduction du nom du mois de l'événement
        month_name = dtstart.strftime('%B')
        month_name = month_translation.get(month_name, month_name)
        if month_name in session_counts:
            # Incrémentation du compteur pour le mois correspondant
            session_counts[month_name] += 1

# Création des données pour le graphique
# Extraction des clés et valeurs du dictionnaire pour les utiliser comme données du graphique
x_labels = list(session_counts.keys())
y_values = list(session_counts.values())

# Création du diagramme en bâtons
plt.figure(figsize=(10, 6))
plt.bar(x_labels, y_values, color='skyblue')
plt.title('Nombre de séances de TP (Septembre-Décembre 2023)', fontsize=14)
plt.xlabel('Mois', fontsize=12)
plt.ylabel('Nombre de séances', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Exportation en PNG
# Enregistrement du graphique au format PNG. Vous pouvez vérifier si le fichier existe déjà pour éviter de l'écraser.
output_file = 'seances_tp.png'
plt.savefig(output_file)
plt.show()

print(f"Graphique exporté sous le nom {output_file}.")
