#!/bin/sh
ROL="$1"
GW="$2"

servicios_comunes() {
    dropbear -R -p 22
    telnetd -p 23 -l /bin/login
}

case "$ROL" in
    fw)
        aplicar >/dev/null || echo "ERROR: no se han podido cargar /reglas/reglas.nft"
        ;;
    cliente)
        ip route replace default via "$GW"
        dropbear -R -p 22
        ;;
    servidor)
        ip route replace default via "$GW"
        servicios_comunes
        httpd -p 80 -h /www/dmz
        openssl s_server -quiet -accept 443 -cert /etc/lab/cert.pem -key /etc/lab/key.pem -www >/dev/null 2>&1 &
        ;;
    plc)
        ip route replace default via "$GW"
        servicios_comunes
        httpd -p 80 -h /www/plc
        python3 /opt/plc.py &
        ;;
    *)
        exec "$@"
        ;;
esac

echo "$(hostname) listo"
exec sleep infinity
