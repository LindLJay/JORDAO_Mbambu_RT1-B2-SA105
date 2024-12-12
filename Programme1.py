import csv

def lire_fichier_ics(nom_fichier):
    with open(nom_fichier, 'r') as fichier:
        lignes = fichier.readlines()
    return lignes

def traiter_contenu_ics(lignes):
    evenement = {}
    for ligne in lignes:
        if ligne.startswith("BEGIN:VEVENT"):
            evenement = {}
        elif ligne.startswith("END:VEVENT"):
            yield evenement
        else:
            cle, valeur = ligne.strip().split(':', 1)
            evenement[cle] = valeur

def ecrire_csv(nom_fichier, evenements):
    with open(nom_fichier, 'w', newline='') as fichier_csv:
        champs = ['DTSTAMP', 'DTSTART', 'DTEND', 'SUMMARY', 'LOCATION', 'DESCRIPTION', 'UID', 'CREATED', 'LAST-MODIFIED', 'SEQUENCE']
        writer = csv.DictWriter(fichier_csv, fieldnames=champs)
        writer.writeheader()
        for evenement in evenements:
            writer.writerow(evenement)

lignes = lire_fichier_ics('evenementSAE_15GroupeA1.ics')
evenements = traiter_contenu_ics(lignes)
ecrire_csv('evenementSAE_15GroupeA1.csv', evenements)
