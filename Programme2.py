import re
from datetime import datetime

def parse_ics_to_csv(file_path):
    """
    Lit un fichier ICS contenant plusieurs événements et les convertit en pseudo-CSV.
    Chaque ligne correspond à un événement unique, avec des valeurs séparées par des points-virgules.
    """
    # Lire le contenu du fichier ICS
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Expression régulière pour capturer tous les blocs d'événements dans le fichier
    event_pattern = re.compile(r'BEGIN:VEVENT(.*?)END:VEVENT', re.DOTALL)
    events = event_pattern.findall(content)  # Trouve tous les événements dans le fichier

    if not events:
        # Si aucun événement n'est trouvé, on lève une erreur
        raise ValueError("Aucun événement trouvé dans le fichier ICS.")

    # Liste pour stocker les lignes pseudo-CSV de tous les événements
    csv_lines = []

    # Liste des en-têtes pour les colonnes pseudo-CSV
    csv_headers = ['UID', 'DATE', 'HEURE', 'DUREE', 'MODALITE', 'SUMMARY', 'LOCATION', 'PROFESSEURS', 'GROUPES']

    # Parcourir chaque événement extrait
    for event in events:
        # Initialiser un dictionnaire avec des valeurs par défaut "vide" pour chaque colonne
        csv_data = {header: "vide" for header in csv_headers}

        # Définir les expressions régulières pour extraire les données importantes
        patterns = {
            'UID': r'UID:(\S+)',  # Correspond à la ligne contenant l'identifiant unique de l'événement
            'DTSTART': r'DTSTART:(\d{8}T\d{6}Z)',  # Date et heure de début
            'DTEND': r'DTEND:(\d{8}T\d{6}Z)',  # Date et heure de fin
            'SUMMARY': r'SUMMARY:(.+)',  # Résumé de l'événement
            'LOCATION': r'LOCATION:(.+)',  # Lieu de l'événement
            'DESCRIPTION': r'DESCRIPTION:(.+)'  # Description contenant des détails supplémentaires
        }

        # Extraire les données de l'événement en utilisant les expressions régulières
        extracted_data = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, event)
            if match:
                # Si une correspondance est trouvée, l'ajouter au dictionnaire des données extraites
                extracted_data[key] = match.group(1).strip()

        # Calculer la durée de l'événement si DTSTART et DTEND sont disponibles
        if 'DTSTART' in extracted_data and 'DTEND' in extracted_data:
            dtstart = datetime.strptime(extracted_data['DTSTART'], '%Y%m%dT%H%M%SZ')  # Convertir DTSTART en objet datetime
            dtend = datetime.strptime(extracted_data['DTEND'], '%Y%m%dT%H%M%SZ')  # Convertir DTEND en objet datetime
            duration = dtend - dtstart  # Calculer la différence entre début et fin

            # Extraire les heures et minutes de la durée
            hours, remainder = divmod(duration.seconds, 3600)
            minutes = remainder // 60
            csv_data['DUREE'] = f"{hours:02}:{minutes:02}"  # Formater la durée en HH:MM

        # Mapper les données extraites aux colonnes pseudo-CSV
        csv_data['UID'] = extracted_data.get('UID', 'vide')  # Identifiant unique

        if 'DTSTART' in extracted_data:
            # Si DTSTART est disponible, extraire la date et l'heure
            dtstart = datetime.strptime(extracted_data['DTSTART'], '%Y%m%dT%H%M%SZ')
            csv_data['DATE'] = dtstart.strftime('%d-%m-%Y')  # Formater la date en JJ-MM-AAAA
            csv_data['HEURE'] = dtstart.strftime('%H:%M')  # Formater l'heure en HH:MM

        # La modalité est supposée être le premier mot du champ SUMMARY
        csv_data['MODALITE'] = extracted_data.get('SUMMARY', 'vide').split(' ')[0] if 'SUMMARY' in extracted_data else 'vide'
        csv_data['SUMMARY'] = extracted_data.get('SUMMARY', 'vide')  # Résumé complet
        csv_data['LOCATION'] = extracted_data.get('LOCATION', 'vide')  # Lieu

        # Extraire les informations sur les professeurs et les groupes à partir de DESCRIPTION
        description = extracted_data.get('DESCRIPTION', '')
        description_parts = description.split('\n')  # Diviser la description par ligne
        if len(description_parts) > 1:
            csv_data['PROFESSEURS'] = description_parts[1]  # Deuxième ligne : professeurs
            csv_data['GROUPES'] = description_parts[0]  # Première ligne : groupes

        # Construire une ligne pseudo-CSV avec les données formatées
        csv_line = (
            f"{csv_data['UID']};{csv_data['DATE']};{csv_data['HEURE']};{csv_data['DUREE']};"
            f"{csv_data['MODALITE']};{csv_data['SUMMARY']};{csv_data['LOCATION']};"
            f"{csv_data['PROFESSEURS']};{csv_data['GROUPES']}"
        )

        # Ajouter la ligne formatée à la liste des résultats
        csv_lines.append(csv_line)

    return csv_lines  # Retourner toutes les lignes pseudo-CSV

# Exemple d'utilisation
file_path = 'ADE_RT1_Septembre2023_Decembre2023.ics'  # Remplacez par le chemin de votre fichier ICS
try:
    pseudo_csv_lines = parse_ics_to_csv(file_path)
    print("Pseudo-CSV:")
    for line in pseudo_csv_lines:
        # Afficher chaque ligne pseudo-CSV pour vérification
        print(line)
except Exception as e:
    # Gérer les erreurs et afficher un message approprié
    print("Erreur:", e)
