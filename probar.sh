#!/bin/sh
# Prueba desde este equipo todos los servicios del laboratorio.

prueba() {
    destino="$1"; servicio="$2"; puerto="$3"
    if [ "$puerto" = "icmp" ]; then
        ping -c 1 -W 2 "$destino" >/dev/null 2>&1 && r="ABIERTO" || r="bloqueado"
    else
        nc -z -w 2 "$destino" "$puerto" >/dev/null 2>&1 && r="ABIERTO" || r="bloqueado"
    fi
    printf "  %-10s %-16s %s\n" "$destino" "$servicio" "$r"
}

echo "Pruebas desde $(hostname)"
printf "  %-10s %-16s %s\n" "DESTINO" "SERVICIO" "RESULTADO"
for d in srv-dmz plc; do
    [ "$(hostname)" = "$d" ] && continue
    prueba "$d" "ping"          icmp
    prueba "$d" "ssh (22)"      22
    prueba "$d" "telnet (23)"   23
    prueba "$d" "http (80)"     80
    if [ "$d" = "srv-dmz" ]; then
        prueba "$d" "https (443)" 443
    else
        prueba "$d" "modbus (502)" 502
    fi
done
if [ "$(hostname)" != "pc-oficina" ]; then
    prueba pc-oficina "ping" icmp
    prueba pc-oficina "ssh (22)" 22
fi
