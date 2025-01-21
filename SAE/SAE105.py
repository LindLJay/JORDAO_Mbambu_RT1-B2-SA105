# Importation des modules nécessaires
import re  # Pour les expressions régulières
from collections import Counter, defaultdict  # Pour compter les occurrences et gérer des dictionnaires
import csv  # Pour lire et écrire des fichiers CSV
import matplotlib.pyplot as plt  # Pour générer des graphiques
import markdown  # Pour convertir du Markdown en HTML
from flask import Flask, render_template_string, request  # Pour créer une application web
import os  # Pour interagir avec le système de fichiers

# Création du dossier 'static' s'il n'existe pas
# Ce dossier est utilisé pour stocker les images des graphiques générés
if not os.path.exists("static"):
    os.makedirs("static")

# Définition des fichiers d'entrée et de sortie
input_file = "DumpFile.txt"  # Fichier contenant les données de capture réseau
markdown_output = "Resumé_Markdown.md"  # Fichier de sortie pour le résumé en Markdown
csv_output = "Donnees_csv.csv"  # Fichier de sortie pour les données extraites au format CSV

# Modèle HTML pour l'application Flask
html_template = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://bootswatch.com/5/slate/bootstrap.min.css">
    <title>SAE105 - Analyse Tcpdump</title>
</head>
<body>
    <div class="container mt-5">
        <h1 class="mb-4">Analyse du trafic réseau</h1>
        <form method="POST" class="mb-4">
            <div class="row">
                <div class="col-md-6">
                    <label for="ip_filter">Filtrer par adresse IP :</label>
                    <input type="text" id="ip_filter" name="ip_filter" class="form-control mb-3">
                </div>
                <div class="col-md-6">
                    <label for="port_filter">Filtrer par port :</label>
                    <input type="text" id="port_filter" name="port_filter" class="form-control mb-3">
                </div>
            </div>
            <button type="submit" class="btn btn-primary">Appliquer les filtres</button>
        </form>
        {{ content | safe }}
        <h2 class="mt-5">Visualisations</h2>
        <div class="d-flex flex-wrap justify-content-between">
            <div class="m-2">
                <img src="/static/top_ips.png" alt="Top IPs" class="img-thumbnail">
                <p class="text-center">Top 10 des adresses IP</p>
            </div>
            <div class="m-2">
                <img src="/static/top_ports.png" alt="Top Ports" class="img-thumbnail">
                <p class="text-center">Top 10 des ports</p>
            </div>
            <div class="m-2">
                <img src="/static/port_distribution.png" alt="Port Distribution" class="img-thumbnail">
                <p class="text-center">Répartition des ports</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

# Expressions régulières pour extraire les données
ip_pattern = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")  # Pour capturer les adresses IP
time_pattern = re.compile(r"(\d{2}:\d{2}:\d{2}\.\d{6})")  # Pour capturer les timestamps
port_pattern = re.compile(r"(?<=\.)\d{1,5}(?=[:\s])")  # Pour capturer les numéros de port
suspicious_ports = {22, 80, 443, 50019}  # Ports considérés comme suspects

# Collecte des données
ip_counter = Counter()  # Compteur pour les occurrences de chaque adresse IP
port_counter = Counter()  # Compteur pour les occurrences de chaque port
suspicious_logs = []  # Liste pour stocker les lignes suspectes
ip_time_intervals = defaultdict(lambda: {"first_seen": None, "last_seen": None})  # Pour stocker les intervalles de temps des IP
activity_analysis = []  # Liste pour stocker les activités suspectes avec des détails

# Analyse du fichier
print("Analyse du fichier pour trouver les adresses IP, les ports et les activités suspectes...")
with open(input_file, "r") as file:
    for line in file:
        # Extraction des données importantes
        time_match = time_pattern.search(line)
        timestamp = time_match.group(1) if time_match else "Inconnu"  # Récupère le timestamp
        ips = ip_pattern.findall(line)  # Récupère toutes les adresses IP dans la ligne
        ports = port_pattern.findall(line)  # Récupère tous les ports dans la ligne

        # Comptabilisation des IPs et ports
        if ips:
            for ip in ips:
                ip_counter.update([ip])  # Met à jour le compteur pour cette IP
                if not ip_time_intervals[ip]["first_seen"]:
                    ip_time_intervals[ip]["first_seen"] = timestamp  # Enregistre la première apparition
                ip_time_intervals[ip]["last_seen"] = timestamp  # Met à jour la dernière apparition

        if ports:
            port_counter.update(ports)  # Met à jour le compteur pour chaque port

        # Détection des activités suspectes
        for port in ports:
            if int(port) in suspicious_ports:  # Si le port est suspect
                suspicious_logs.append(line.strip())  # Ajoute la ligne à la liste des logs suspects
                activity_analysis.append({
                    "timestamp": timestamp,
                    "event": "Connexion suspecte détectée",
                    "details": line.strip(),
                    "reason": f"Port critique utilisé ({port})"
                })  # Enregistre l'activité suspecte

# Génération du fichier Markdown
markdown_content = "# Analyse du trafic réseau\n\n"
markdown_content += "## Top 10 des adresses IP\n"
for ip, count in ip_counter.most_common(10):  # Pour les 10 IP les plus fréquentes
    first_seen = ip_time_intervals[ip]["first_seen"]
    last_seen = ip_time_intervals[ip]["last_seen"]
    markdown_content += f"- **{ip}** : {count} occurrences (Première apparition : {first_seen}, Dernière apparition : {last_seen})\n"

markdown_content += "\n## Top 10 des ports\n"
for port, count in port_counter.most_common(10):  # Pour les 10 ports les plus utilisés
    markdown_content += f"- **Port {port}** : {count} occurrences\n"

markdown_content += "\n## Analyse détaillée des activités suspectes\n"
if activity_analysis:  # Si des activités suspectes ont été détectées
    for activity in activity_analysis:
        markdown_content += f"- **{activity['timestamp']}** : {activity['event']}\n"
        markdown_content += f"  - Détails : `{activity['details']}`\n"
        markdown_content += f"  - Raison : {activity['reason']}\n\n"
else:
    markdown_content += "Aucune activité suspecte détectée.\n"

# Écriture du fichier Markdown
with open(markdown_output, "w") as md_file:
    md_file.write(markdown_content)

# Fonction pour extraire les données TCPDUMP
def extract_tcpdump_data(file_path):
    try:
        with open(file_path, encoding="utf8") as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Le fichier n'existe pas à l'emplacement {os.path.abspath(file_path)}")
        return None

    data = []

    for line in lines:
        if "Flags" in line:  # Vérifie la présence d'un flag dans la ligne
            parts = line.split()
            if len(parts) >= 9:  # Vérifie qu'il y a suffisamment d'informations
                timestamp = parts[0]
                src_ip = parts[2]
                dst_ip = parts[4]
                flag = parts[6]

                # Recherche de la longueur du paquet à partir de "length"
                length = "N/A"
                if "length" in line:  # Vérifie si "length" est présent dans la ligne
                    try:
                        length_index = parts.index("length") + 1
                        if length_index < len(parts):
                            length = parts[length_index]  # Récupère la valeur après "length"
                    except ValueError:
                        length = "N/A"  # Si "length" n'est pas dans parts, on garde "N/A"

                # Ajout des données dans la liste
                data.append([timestamp, src_ip, dst_ip, flag, length])

    return data

# Fonction pour sauvegarder les données dans un fichier CSV
def save_to_csv(data, csv_filename):
    headers = ['Temps', 'IP Source', 'IP Destination', 'Flag', 'Longueur du Paquet']

    with open(csv_filename, mode='w', newline='', encoding='utf8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)

# Extraction des données TCPDUMP et sauvegarde en CSV
tcpdump_data = extract_tcpdump_data(input_file)
if tcpdump_data:
    save_to_csv(tcpdump_data, csv_output)

# Génération de graphiques
# Graphique pour les 10 IP les plus fréquentes
top_ips = ip_counter.most_common(10)
ips, counts = zip(*top_ips) if top_ips else ([], [])
plt.bar(ips, counts)
plt.xlabel("IP Addresses")
plt.ylabel("Occurrences")
plt.title("Top 10 IP Addresses")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("static/top_ips.png")  # Sauvegarde du graphique
plt.close()

# Graphique en camembert pour la répartition des ports
port_distribution = port_counter.most_common(10)
labels = [f"Port {port}" for port, _ in port_distribution]
sizes = [count for _, count in port_distribution]

if sizes:
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title("Port Distribution")
    plt.savefig("static/port_distribution.png")  # Sauvegarde du graphique
    plt.close()

# Fonction pour générer le graphique des Top 10 des ports
def plot_top_ports(port_counter, output_file):
    top_ports = port_counter.most_common(10)
    ports, counts = zip(*top_ports)

    plt.figure(figsize=(10, 6))
    plt.bar(ports, counts, color='orange')
    plt.xlabel('Ports')
    plt.ylabel('Nombre d\'occurrences')
    plt.title('Top 10 des ports')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

# Générer le graphique des Top 10 des ports
plot_top_ports(port_counter, "static/top_ports.png")

# Application Flask
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def display_results():
    ip_filter = request.form.get("ip_filter", "")  # Récupère le filtre IP du formulaire
    port_filter = request.form.get("port_filter", "")  # Récupère le filtre port du formulaire

    with open(markdown_output, "r") as md_file:
        markdown_text = md_file.read()

    filtered_content = []
    for line in markdown_text.split("\n"):  # Filtre les lignes en fonction des filtres
        if ip_filter and ip_filter not in line:
            continue
        if port_filter and port_filter not in line:
            continue
        filtered_content.append(line)

    markdown_text = "\n".join(filtered_content)
    html_content = markdown.markdown(markdown_text)  # Convertit le Markdown en HTML

    return render_template_string(html_template, content=html_content)  # Affiche le contenu dans le modèle HTML

if __name__ == "__main__":
    app.run(debug=True)  # Lance l'application Flask