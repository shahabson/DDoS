███╗   ██╗███████╗████████╗██████╗  ██████╗ ████████╗
████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██╔═══██╗╚══██╔══╝
██╔██╗ ██║█████╗     ██║   ██████╔╝██║   ██║   ██║   
██║╚██╗██║██╔══╝     ██║   ██╔═══╝ ██║   ██║   ██║   
██║ ╚████║███████╗   ██║   ██║     ╚██████╔╝   ██║   
╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝      ╚═════╝    ╚═╝   

           NetBot v2.2 – Advanced C2 + Botnet
     ⚠️ For Education, Red Team, and Research Use Only

---

## 🚀 Overview

**NetBot v2.2** is a modular **Command & Control (C2)** and **botnet client** framework built for:

- Cybersecurity education
- Red team simulations
- Research on DDoS tactics and detection

It demonstrates modern, multi-layer **denial-of-service** techniques and supports encrypted traffic, randomized payloads, and raw socket attacks.

---

## 🧠 Capabilities

| Layer | Attack Type                            | Encrypted | Notes |
|:------|:----------------------------------------|:----------|:------|
| L7    | HTTP Flood (GET/POST/Random)            | ✅ (HTTPS) | Custom headers, randomized paths |
| L7    | Slowloris (Slow HTTP headers)           | ✅         | Includes SSL variant |
| L4    | TCP Connect Flood                       | ✅         | Normal & wrapped in TLS |
| L4    | TCP SYN Flood (raw socket)              | ❌         | Randomized stealthy packets |
| L4    | UDP Flood (coming soon)                 | ❌         | High-bandwidth overload |
| L3    | ICMP Flood (raw Echo requests)          | ❌         | Requires root/admin |
| L3    | Ping Flood (system ping)                | ❌         | Basic |

---

## 📦 File Structure

```
NetBot/
├── netbot_client.py       # Bot client – executes attack logic
├── netbot_server.py       # C2 command & control server
├── README.md              # This file
```

---

## 🛠 Requirements

- Python 3.x
- Linux or Windows (Linux preferred for raw sockets)
- `sudo` or admin rights for some attacks

---

## ⚙️ Setup & Usage

### 📍 C2 Server (Control Panel)

```bash
python3 netbot_server.py
```

You’ll be greeted with a command prompt:
```bash
C2 > launch_httpflood
```

### 🤖 Bot Client

```bash
sudo python3 netbot_client.py
```

> 💡 Bots automatically connect to the C2 server and await instructions.

---

## 📚 Command Reference

```
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
```

---

## 🔐 Legal Disclaimer

> ⚠️ This tool is intended for **authorized security testing, educational use, and controlled lab environments**.  
> Any unauthorized use against live systems without permission is likely **illegal** and **unethical**.  
> You assume all responsibility for use or misuse of this code.

---

## 📄 License

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction...

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY.
