import re
from collections import Counter
import csv
import matplotlib.pyplot as plt
import markdown
from flask import Flask, render_template_string
import os
# Créer le dossier 'static' s'il n'existe pas
if not os.path.exists("static"):
    os.makedirs("static")


# Fichiers d'entrée et de sortie
input_file = "fichier1000.txt"  # Fichier d'entrée contenant les logs réseau
markdown_output = "Resumé_Markdown.md"  # Fichier Markdown de sortie
csv_output = "Données_csv.csv"  # Fichier CSV de sortie

# Modèle HTML Flask
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://bootswatch.com/5/slate/bootstrap.min.css">
    <title>SAE105-Analyse Tcpdump</title>
</head>
<body>
    <div style="margin: 20px;">
        {{ content | safe }}
    </div>
</body>
</html>
"""

# Expressions régulières pour extraire les IP et les ports
ip_pattern = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")  # Correspond à toute IP valide
port_pattern = re.compile(r"(?<=\.)\d{1,5}(?=:)")  # Correspond à tout port entre un point et un deux-points
suspicious_ports = {22, 80, 443, 50019}  # Ports suspects à surveiller

# Collecte des données
ip_counter = Counter()  # Compteur pour les adresses IP
port_counter = Counter()  # Compteur pour les ports
suspicious_activities = []  # Liste pour stocker les activités suspectes

# Analyse du fichier texte
print("Analyzing the file for IPs and ports...")
with open(input_file, "r") as file:
    for line in file:
        # Extraction des adresses IP
        ips = ip_pattern.findall(line)
        if ips:
            ip_counter.update(ips)

        # Extraction des ports
        ports = port_pattern.findall(line)
        if ports:
            port_counter.update(ports)
            for port in ports:
                if int(port) in suspicious_ports:
                    suspicious_activities.append(line.strip())

# Génération de graphiques
# Graphique pour les 10 IP les plus fréquentes
top_ips = ip_counter.most_common(10)
ips, counts = zip(*top_ips)
plt.bar(ips, counts)
plt.xlabel("IP Addresses")
plt.ylabel("Occurrences")
plt.title("Top 10 IP Addresses")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("static/top_ips.png")  # Sauvegarde du graphique
plt.close()

# Graphique pour les 10 ports les plus fréquents
top_ports = port_counter.most_common(10)
ports, counts = zip(*top_ports)
plt.bar(ports, counts)
plt.xlabel("Ports")
plt.ylabel("Occurrences")
plt.title("Top 10 Ports")
plt.tight_layout()
plt.savefig("static/top_ports.png")  # Sauvegarde du graphique
plt.close()

# Génération de Markdown
markdown_content = "# Network Traffic Analysis\n\n"

# Section pour les 10 IP les plus fréquentes
markdown_content += "## Top 10 IP Addresses\n"
for ip, count in top_ips:
    markdown_content += f"- **{ip}**: {count} occurrences\n"

# Section pour les 10 ports les plus fréquents
markdown_content += "\n## Top 10 Ports\n"
for port, count in top_ports:
    markdown_content += f"- **Port {port}**: {count} occurrences\n"

# Section pour les activités suspectes
markdown_content += "\n## Suspicious Activities\n"
if suspicious_activities:
    for activity in suspicious_activities[:10]:  # Limite à 10 activités suspectes
        markdown_content += f"- `{activity}`\n"
else:
    markdown_content += "No suspicious activities detected.\n"

# Écriture du fichier Markdown
with open(markdown_output, "w") as md_file:
    md_file.write(markdown_content)

# Export des données en CSV
with open(csv_output, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["IP Address", "Occurrences"])  # En-tête pour les IP
    for ip, count in ip_counter.most_common():
        writer.writerow([ip, count])

    writer.writerow([])  # Ligne vide pour séparer les sections
    writer.writerow(["Port", "Occurrences"])  # En-tête pour les ports
    for port, count in port_counter.most_common():
        writer.writerow([port, count])

# Conversion Markdown en HTML avec Flask
app = Flask(__name__)

@app.route("/")
def display_results():
    with open(markdown_output, "r") as md_file:
        markdown_text = md_file.read()
    html_content = markdown.markdown(markdown_text)

    # Ajout des graphiques à la page web
    html_content += '<h2>Graphiques</h2>'
    html_content += '<img src="/static/top_ips.png" alt="Top IPs">'
    html_content += '<img src="/static/top_ports.png" alt="Top Ports">'

    return render_template_string(html_template, content=html_content)

if __name__ == "__main__":
    app.run(debug=True)