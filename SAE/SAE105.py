import re
from collections import Counter, defaultdict
import csv
import matplotlib.pyplot as plt
import markdown
from flask import Flask, render_template_string, request
import os

# Créer le dossier 'static' s'il n'existe pas
if not os.path.exists("static"):
    os.makedirs("static")

# Fichiers d'entrée et de sortie
input_file = "fichier1000.txt"
markdown_output = "Resumé_Markdown.md"
csv_output = "Donnees_csv.csv"

# Modèle HTML Flask
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
ip_pattern = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
time_pattern = re.compile(r"(\d{2}:\d{2}:\d{2}\.\d{6})")  # Format de l'heure
port_pattern = re.compile(r"(?<=\.)\d{1,5}(?=[:\s])")
dns_pattern = re.compile(r"PTR\?.*\.in-addr\.arpa")
suspicious_ports = {22, 80, 443, 50019}  # Ports à surveiller

# Collecte des données
ip_counter = Counter()
port_counter = Counter()
dns_queries = []
suspicious_logs = []
ip_time_intervals = defaultdict(
    lambda: {"first_seen": None, "last_seen": None})  # Pour les IPs et leurs intervalles de temps

# Analyse avancée
activity_analysis = []

print("Analyse du fichier pour trouver les adresses IP, les ports et les activités suspectes...")
with open(input_file, "r") as file:
    for line in file:
        # Extraction des données importantes
        time_match = time_pattern.search(line)
        timestamp = time_match.group(1) if time_match else "Inconnu"
        ips = ip_pattern.findall(line)
        ports = port_pattern.findall(line)

        # Comptabilisation des IPs et ports
        if ips:
            for ip in ips:
                ip_counter.update([ip])
                if not ip_time_intervals[ip]["first_seen"]:
                    ip_time_intervals[ip]["first_seen"] = timestamp
                ip_time_intervals[ip]["last_seen"] = timestamp

        if ports:
            port_counter.update(ports)

        # Analyse des activités suspectes
        if dns_pattern.search(line):
            dns_queries.append(line.strip())
            activity_analysis.append({
                "timestamp": timestamp,
                "event": "Requête DNS inverse détectée",
                "details": line.strip(),
                "reason": "Recherche PTR sur une adresse IP"
            })

        for port in ports:
            if int(port) in suspicious_ports:
                suspicious_logs.append(line.strip())
                activity_analysis.append({
                    "timestamp": timestamp,
                    "event": "Connexion suspecte détectée",
                    "details": line.strip(),
                    "reason": f"Port critique utilisé ({port})"
                })

# Génération de Markdown
markdown_content = "# Analyse du trafic réseau\n\n"
markdown_content += "## Top 10 des adresses IP\n"
for ip, count in ip_counter.most_common(10):
    first_seen = ip_time_intervals[ip]["first_seen"]
    last_seen = ip_time_intervals[ip]["last_seen"]
    markdown_content += f"- **{ip}** : {count} occurrences (Première apparition : {first_seen}, Dernière apparition : {last_seen})\n"

markdown_content += "\n## Top 10 des ports\n"
for port, count in port_counter.most_common(10):
    markdown_content += f"- **Port {port}** : {count} occurrences\n"

markdown_content += "\n## Analyse détaillée des activités suspectes\n"
if activity_analysis:
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

# Flask App
app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def display_results():
    ip_filter = request.form.get("ip_filter", "")
    port_filter = request.form.get("port_filter", "")

    with open(markdown_output, "r") as md_file:
        markdown_text = md_file.read()

    filtered_content = []
    for line in markdown_text.split("\n"):
        if ip_filter and ip_filter not in line:
            continue
        if port_filter and port_filter not in line:
            continue
        filtered_content.append(line)

    markdown_text = "\n".join(filtered_content)
    html_content = markdown.markdown(markdown_text)

    return render_template_string(html_template, content=html_content)


if __name__ == "__main__":
    app.run(debug=True)