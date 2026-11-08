#!/usr/bin/env python3
"""PLC simulado: servidor Modbus TCP (puerto 502) que controla un depósito."""
import socketserver
import struct
import threading
import time

# 0 nivel del depósito (%), 1 consigna de nivel (%), 2 bomba (0/1), 3 alarma (0/1)
regs = [50, 60, 0, 0, 0, 0, 0, 0, 0, 0]
lock = threading.Lock()


def proceso():
    while True:
        time.sleep(1)
        with lock:
            regs[2] = 1 if regs[0] < regs[1] else 0
            regs[0] = max(0, min(100, regs[0] + (2 if regs[2] else -1)))
            regs[3] = 1 if regs[0] >= 95 else 0


class Modbus(socketserver.BaseRequestHandler):
    def handle(self):
        while True:
            head = self.request.recv(7)
            if len(head) < 7:
                return
            tid, _, length, unit = struct.unpack(">HHHB", head)
            pdu = self.request.recv(length - 1)
            fc = pdu[0]
            with lock:
                if fc == 3 and len(pdu) >= 5:
                    start, count = struct.unpack(">HH", pdu[1:5])
                    if start + count > len(regs) or count == 0:
                        resp = bytes([0x83, 2])
                    else:
                        vals = regs[start:start + count]
                        resp = bytes([3, 2 * count]) + struct.pack(f">{count}H", *vals)
                elif fc == 6 and len(pdu) >= 5:
                    addr, val = struct.unpack(">HH", pdu[1:5])
                    if addr >= len(regs):
                        resp = bytes([0x86, 2])
                    else:
                        regs[addr] = val
                        resp = pdu[:5]
                else:
                    resp = bytes([fc | 0x80, 1])
            self.request.sendall(struct.pack(">HHHB", tid, 0, len(resp) + 1, unit) + resp)


class Servidor(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    threading.Thread(target=proceso, daemon=True).start()
    Servidor(("0.0.0.0", 502), Modbus).serve_forever()
