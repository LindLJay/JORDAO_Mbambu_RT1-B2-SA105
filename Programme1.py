import re

def parse_ics_to_csv(file_path):
    """
    Lis un fichier ICS contenant un événement et le convertit en pseudo-CSV.

    :param file_path: Chemin vers le fichier ICS
    :return: Chaîne de caractères au format pseudo-CSV
    """
    # Lire le fichier ICS
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Expression régulière pour extraire un événement unique
    event_pattern = re.compile(r'BEGIN:VEVENT(.*?)END:VEVENT', re.DOTALL)
    event_match = event_pattern.search(content)

    if not event_match:
        raise ValueError("Aucun événement trouvé dans le fichier ICS.")

    event = event_match.group(1)

    # Dictionnaire des clés ICS et leurs équivalents en pseudo-CSV
    csv_data = {
        'UID': None,
        'DTSTART': None,
        'DUREE': None,
        'MODALITE': None,
        'SUMMARY': None,
        'LOCATION': None,
        'PROFESSEURS': None,
        'GROUPES': None
    }

    # Extraire les informations nécessaires
    patterns = {
        'UID': r'UID:(\S+)',
        'DTSTART': r'DTSTART:(\d{8}T\d{6}Z)',
        'DTEND': r'DTEND:(\d{8}T\d{6}Z)',
        'SUMMARY': r'SUMMARY:(.+)',
        'LOCATION': r'LOCATION:(.+)',
        'DESCRIPTION': r'DESCRIPTION:(.+)'
    }

    extracted_data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, event)
        if match:
            extracted_data[key] = match.group(1).strip()

    # Calculer la durée (DTEND - DTSTART)
    if 'DTSTART' in extracted_data and 'DTEND' in extracted_data:
        from datetime import datetime

        dtstart = datetime.strptime(extracted_data['DTSTART'], '%Y%m%dT%H%M%SZ')
        dtend = datetime.strptime(extracted_data['DTEND'], '%Y%m%dT%H%M%SZ')
        duration = dtend - dtstart

        hours, remainder = divmod(duration.seconds, 3600)
        minutes = remainder // 60
        csv_data['DUREE'] = f"{hours:02}:{minutes:02}"

    # Mapper les données extraites aux clés pseudo-CSV
    csv_data['UID'] = extracted_data.get('UID', '')

    if 'DTSTART' in extracted_data:
        dtstart = datetime.strptime(extracted_data['DTSTART'], '%Y%m%dT%H%M%SZ')
        csv_data['DATE'] = dtstart.strftime('%d-%m-%Y')
        csv_data['HEURE'] = dtstart.strftime('%H:%M')

    csv_data['MODALITE'] = extracted_data.get('SUMMARY', '').split(' ')[0]  # Supposons que la modalité soit le premier mot de SUMMARY
    csv_data['SUMMARY'] = extracted_data.get('SUMMARY', '')
    csv_data['LOCATION'] = extracted_data.get('LOCATION', '')

    # Extraction des professeurs et groupes à partir de DESCRIPTION
    description = extracted_data.get('DESCRIPTION', '')
    description_parts = description.split('\n')
    if len(description_parts) > 1:
        csv_data['PROFESSEURS'] = description_parts[1]
        csv_data['GROUPES'] = description_parts[0]

    # Construire la chaîne pseudo-CSV
    csv_line = (
        f"{csv_data['UID']};{csv_data['DATE']};{csv_data['HEURE']};{csv_data['DUREE']};"
        f"{csv_data['MODALITE']};{csv_data['SUMMARY']};{csv_data['LOCATION']};"
        f"{csv_data['PROFESSEURS']};{csv_data['GROUPES']}"
    )

    return csv_line

# Exemple d'utilisation
file_path = 'evenementSAE_15GroupeA1.ics'  # Remplacez par le chemin de votre fichier ICS
try:
    pseudo_csv = parse_ics_to_csv(file_path)
    print("Pseudo-CSV:", pseudo_csv)
except Exception as e:
    print("Erreur:", e)
