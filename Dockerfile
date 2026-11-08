FROM alpine:3.20

RUN apk add --no-cache nftables iproute2 iputils curl netcat-openbsd nmap nmap-scripts \
        tcpdump python3 openssl dropbear busybox-extras \
 && adduser -D operador && echo "operador:operador" | chpasswd \
 && mkdir -p /etc/lab /etc/dropbear \
 && openssl req -x509 -newkey rsa:2048 -nodes -days 3650 -subj "/CN=lab" \
        -keyout /etc/lab/key.pem -out /etc/lab/cert.pem 2>/dev/null

COPY arranque.sh /usr/local/bin/arranque
COPY probar.sh /usr/local/bin/probar
COPY aplicar.sh /usr/local/bin/aplicar
COPY modbus.py /usr/local/bin/modbus
COPY plc.py /opt/plc.py
COPY www /www
RUN sed -i "s/\r$//" /usr/local/bin/* /opt/plc.py && chmod +x /usr/local/bin/*

ENTRYPOINT ["/usr/local/bin/arranque"]
