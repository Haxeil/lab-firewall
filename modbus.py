#!/usr/bin/env python3
"""Cliente Modbus TCP mínimo.

  modbus leer IP                 lee los registros 0-3 del PLC
  modbus escribir IP REG VALOR   escribe un registro (función 6)
"""
import socket
import struct
import sys

NOMBRES = ["nivel del depósito (%)", "consigna de nivel (%)", "bomba (1=marcha)", "alarma de rebose"]


def peticion(ip, pdu):
    with socket.create_connection((ip, 502), timeout=3) as s:
        s.sendall(struct.pack(">HHHB", 1, 0, len(pdu) + 1, 1) + pdu)
        head = s.recv(7)
        _, _, length, _ = struct.unpack(">HHHB", head)
        return s.recv(length - 1)


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("leer", "escribir"):
        sys.exit(__doc__)
    ip = sys.argv[2]
    try:
        if sys.argv[1] == "leer":
            r = peticion(ip, struct.pack(">BHH", 3, 0, 4))
            for i, v in enumerate(struct.unpack(">4H", r[2:10])):
                print(f"  registro {i}  {NOMBRES[i]:<24} = {v}")
        else:
            reg, val = int(sys.argv[3]), int(sys.argv[4])
            r = peticion(ip, struct.pack(">BHH", 6, reg, val))
            print(f"  registro {reg} = {val}  (escrito)" if r[0] == 6 else f"  error Modbus {r[1]}")
    except (socket.timeout, TimeoutError):
        sys.exit("  sin respuesta: tiempo agotado (¿lo está bloqueando el firewall?)")
    except OSError as e:
        sys.exit(f"  error de conexión: {e}")


if __name__ == "__main__":
    main()
