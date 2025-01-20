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
port_pattern = re.compile(r"(?<=\.)\d{1,5}(?=[:\s])")
dns_pattern = re.compile(r"PTR\?.*\.in-addr\.arpa")
suspicious_ports = {22, 80, 443, 50019}

# Collecte des données
ip_counter = Counter()
port_counter = Counter()
dns_queries = []
suspicious_logs = []

print("Analyse du fichier pour trouver les adresses IP, les ports et les activités suspectes...")
with open(input_file, "r") as file:
    for line in file:
        ips = ip_pattern.findall(line)
        if ips:
            ip_counter.update(ips)

        ports = port_pattern.findall(line)
        if ports:
            port_counter.update(ports)

        if dns_pattern.search(line):
            dns_queries.append(line.strip())

        for port in ports:
            if int(port) in suspicious_ports:
                suspicious_logs.append(line.strip())

# Graphiques
# Top 10 des IPs
top_ips = ip_counter.most_common(10)
ips, counts = zip(*top_ips) if top_ips else ([], [])
plt.bar(ips, counts, color="skyblue")
plt.xlabel("Adresses IP")
plt.ylabel("Occurrences")
plt.title("Top 10 des adresses IP")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("static/top_ips.png")
plt.close()

# Top 10 des ports
top_ports = port_counter.most_common(10)
ports, counts = zip(*top_ports) if top_ports else ([], [])
plt.bar(ports, counts, color="lightgreen")
plt.xlabel("Ports")
plt.ylabel("Occurrences")
plt.title("Top 10 des ports")
plt.tight_layout()
plt.savefig("static/top_ports.png")
plt.close()

# Répartition des ports (Camembert)
port_distribution = port_counter.most_common(10)
labels = [f"Port {port}" for port, _ in port_distribution]
sizes = [count for _, count in port_distribution]

if sizes:
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140, colors=plt.cm.Paired.colors)
    plt.title("Répartition des ports")
    plt.savefig("static/port_distribution.png")
    plt.close()

# Génération de Markdown
markdown_content = "# Analyse du trafic réseau\n\n"
markdown_content += "## Top 10 des adresses IP\n"
for ip, count in top_ips:
    markdown_content += f"- **{ip}** : {count} occurrences\n"

markdown_content += "\n## Top 10 des ports\n"
for port, count in top_ports:
    markdown_content += f"- **Port {port}** : {count} occurrences\n"

markdown_content += "\n## Requêtes DNS suspectes\n"
if dns_queries:
    markdown_content += "\n".join(f"- `{query}`" for query in dns_queries)
else:
    markdown_content += "Aucune requête DNS suspecte détectée.\n"

markdown_content += "\n## Activités suspectes\n"
if suspicious_logs:
    markdown_content += "\n".join(f"- `{log}`" for log in suspicious_logs[:10])
else:
    markdown_content += "Aucune activité suspecte détectée.\n"

with open(markdown_output, "w") as md_file:
    md_file.write(markdown_content)

# CSV Export
with open(csv_output, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Adresse IP", "Occurrences"])
    for ip, count in ip_counter.most_common():
        writer.writerow([ip, count])
    writer.writerow([])
    writer.writerow(["Port", "Occurrences"])
    for port, count in port_counter.most_common():
        writer.writerow([port, count])
    writer.writerow([])
    writer.writerow(["Logs suspects"])
    for log in suspicious_logs:
        writer.writerow([log])

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
