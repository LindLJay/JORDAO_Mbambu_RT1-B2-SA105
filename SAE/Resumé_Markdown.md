# Analyse du trafic réseau

## Top 10 des adresses IP
- **184.107.43.74** : 82 occurrences (Première apparition : 11:42:06.679971, Dernière apparition : 11:42:06.682619)
- **192.168.190.130** : 12 occurrences (Première apparition : 11:42:04.766656, Dernière apparition : 11:42:06.681222)
- **130.190.168.192** : 1 occurrences (Première apparition : 11:42:05.768334, Dernière apparition : 11:42:05.768334)

## Top 10 des ports
- **Port 50019** : 8 occurrences
- **Port 50245** : 4 occurrences
- **Port 58466** : 2 occurrences
- **Port 53220** : 2 occurrences
- **Port 74** : 1 occurrences
- **Port 2465** : 1 occurrences
- **Port 2466** : 1 occurrences
- **Port 2467** : 1 occurrences
- **Port 2468** : 1 occurrences
- **Port 2469** : 1 occurrences

## Analyse détaillée des activités suspectes
- **11:42:04.766656** : Connexion suspecte détectée
  - Détails : `11:42:04.766656 IP BP-Linux8.ssh > 192.168.190.130.50019: Flags [P.], seq 2243505564:2243505672, ack 1972915080, win 312, options [nop,nop,TS val 102917262 ecr 377952805], length 108`
  - Raison : Port critique utilisé (50019)

- **11:42:04.766694** : Connexion suspecte détectée
  - Détails : `11:42:04.766694 IP BP-Linux8.ssh > 192.168.190.130.50019: Flags [P.], seq 108:144, ack 1, win 312, options [nop,nop,TS val 102917262 ecr 377952805], length 36`
  - Raison : Port critique utilisé (50019)

- **11:42:04.766723** : Connexion suspecte détectée
  - Détails : `11:42:04.766723 IP BP-Linux8.ssh > 192.168.190.130.50019: Flags [P.], seq 144:252, ack 1, win 312, options [nop,nop,TS val 102917262 ecr 377952805], length 108`
  - Raison : Port critique utilisé (50019)

- **11:42:04.766744** : Connexion suspecte détectée
  - Détails : `11:42:04.766744 IP BP-Linux8.ssh > 192.168.190.130.50019: Flags [P.], seq 252:288, ack 1, win 312, options [nop,nop,TS val 102917262 ecr 377952805], length 36`
  - Raison : Port critique utilisé (50019)

- **11:42:04.785366** : Connexion suspecte détectée
  - Détails : `11:42:04.785366 IP 192.168.190.130.50019 > BP-Linux8.ssh: Flags [.], ack 108, win 7319, options [nop,nop,TS val 377953205 ecr 102917262], length 0`
  - Raison : Port critique utilisé (50019)

- **11:42:04.785384** : Connexion suspecte détectée
  - Détails : `11:42:04.785384 IP 192.168.190.130.50019 > BP-Linux8.ssh: Flags [.], ack 144, win 7318, options [nop,nop,TS val 377953205 ecr 102917262], length 0`
  - Raison : Port critique utilisé (50019)

- **11:42:04.785406** : Connexion suspecte détectée
  - Détails : `11:42:04.785406 IP 192.168.190.130.50019 > BP-Linux8.ssh: Flags [.], ack 252, win 7316, options [nop,nop,TS val 377953205 ecr 102917262], length 0`
  - Raison : Port critique utilisé (50019)

- **11:42:04.785454** : Connexion suspecte détectée
  - Détails : `11:42:04.785454 IP 192.168.190.130.50019 > BP-Linux8.ssh: Flags [.], ack 288, win 7320, options [nop,nop,TS val 377953205 ecr 102917262], length 0`
  - Raison : Port critique utilisé (50019)

- **11:42:05.768334** : Requête DNS inverse détectée
  - Détails : `11:42:05.768334 IP BP-Linux8.58466 > ns1.lan.rt.domain: 16550+ PTR? 130.190.168.192.in-addr.arpa. (46)`
  - Raison : Recherche PTR sur une adresse IP

