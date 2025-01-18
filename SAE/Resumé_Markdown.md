# Network Traffic Analysis

## Top 10 IP Addresses
- **184.107.43.74**: 82 occurrences
- **192.168.190.130**: 12 occurrences
- **130.190.168.192**: 1 occurrences

## Top 10 Ports
- **Port 50019**: 4 occurrences
- **Port 50245**: 3 occurrences
- **Port 58466**: 1 occurrences
- **Port 53220**: 1 occurrences

## Suspicious Activities
### Suspicious Port Activity
- Total occurrences: 4
- Example: `11:42:04.766656 IP BP-Linux8.ssh > 192.168.190.130.50019: Flags [P.], seq 2243505564:2243505672, ack 1972915080, win 312, options [nop,nop,TS val 102917262 ecr 377952805], length 108`
### Unusual DNS Query
- Total occurrences: 2
- Example: `11:42:05.768334 IP BP-Linux8.58466 > ns1.lan.rt.domain: 16550+ PTR? 130.190.168.192.in-addr.arpa. (46)`
### Suspicious HTTP Traffic
- Total occurrences: 81
- Example: `11:42:06.681248 IP 190-0-175-100.gba.solunet.com.ar.2465 > 184.107.43.74.http: Flags [S], seq 326991629:326991749, win 512, length 120: HTTP`
### Potential SYN Flood
- Total occurrences: 81
- Example: `11:42:06.681248 IP 190-0-175-100.gba.solunet.com.ar.2465 > 184.107.43.74.http: Flags [S], seq 326991629:326991749, win 512, length 120: HTTP`
