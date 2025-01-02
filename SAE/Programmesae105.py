import re
from collections import Counter
import markdown
from flask import Flask, render_template_string

# Fichiers d'entrée et de sortie
input_file = "fichier1000.txt"
markdown_output = "summary.md"

# Modèle HTML Flask
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Traffic Analysis</title>
</head>
<body>
    <div style="margin: 20px;">
        {{ content | safe }}
    </div>
</body>
</html>
"""

# Expressions régulières mises à jour
ip_pattern = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")  # Correspond à toute IP valide
port_pattern = re.compile(r"(?<=\.)\d{1,5}(?=:)")  # Correspond à tout port entre un point et un deux-points
suspicious_ports = {22, 80, 443, 50019}  # Ports suspects à surveiller

# Collecte des données
ip_counter = Counter()
port_counter = Counter()
suspicious_activities = []

# Analyse du fichier texte
print("Analyzing the file for IPs and ports...")
with open(input_file, "r") as file:
    for line in file:
        # Extraction des IP
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

# Messages de diagnostic
print(f"Total unique IPs found: {len(ip_counter)}")
print(f"Total unique ports found: {len(port_counter)}")
print(f"Total suspicious activities found: {len(suspicious_activities)}")

# Génération de Markdown
markdown_content = "# Network Traffic Analysis\n\n"

# Top 10 IP Addresses
if ip_counter:
    markdown_content += "## Top 10 IP Addresses\n"
    for ip, count in ip_counter.most_common(10):
        markdown_content += f"- **{ip}**: {count} occurrences\n"
else:
    markdown_content += "No IP data found.\n"

# Top 10 Ports
if port_counter:
    markdown_content += "\n## Top 10 Ports\n"
    for port, count in port_counter.most_common(10):
        markdown_content += f"- **Port {port}**: {count} occurrences\n"
else:
    markdown_content += "No port data found.\n"

# Suspicious Activities
if suspicious_activities:
    markdown_content += "\n## Suspicious Activities\n"
    for activity in suspicious_activities[:10]:
        markdown_content += f"- `{activity}`\n"
else:
    markdown_content += "No suspicious activities detected.\n"

with open(markdown_output, "w") as md_file:
    md_file.write(markdown_content)

# Conversion Markdown en HTML avec Flask
app = Flask(__name__)


@app.route("/")
def display_results():
    with open(markdown_output, "r") as md_file:
        markdown_text = md_file.read()
    html_content = markdown.markdown(markdown_text)
    return render_template_string(html_template, content=html_content)


if __name__ == "__main__":
    app.run(debug=True)
