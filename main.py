import asyncio
import socket
import curses
import ipaddress
import time
import os
import sys
from aiohttp import ClientSession, ClientTimeout
from aiohttp_socks import ProxyConnector

# --- کلاس کاملاً مستقل برای انیمیشن بنر تبلیغاتی ---
class BannerAnimator:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.anim_frame = 0
        self.height, self.width = stdscr.getmaxyx()
        
        self.banner = [
            " ╔═════════════════════════════════════════════════════════╗ ",
            " ║ __     __  ____    ____    ____     ____   _   _   ___  ║ ",
            " ║ \\ \\   / / / __ \\  / ___|  / __ \\   / ___| | | | | |_ _| ║ ",
            " ║  \\ \\ / / | |  | | \\___ \\ | |  | | | |  _  | |_| |  | |  ║ ",
            " ║   \\ V /  | |__| |  ___) || |__| | | |_| | |  _  |  | |  ║ ",
            " ║    \\_/    \\____/  |____/  \\____/   \\____| |_| |_| |___| ║ ",
            " ╚═════════════════[ VOSOGHI SCANNER v8.0 ]════════════════╝ "
        ]
        
        self.available_colors = [4, 6, 3, 1, 2]
        self.max_cols = max(len(line) for line in self.banner)
        self.color_shift = 0

    async def start_loop(self):
        while True:
            try:
                if self.anim_frame < self.max_cols:
                    # مرحله ۱: ظاهر شدن ستونی (شبیه موج رادار اسکنر)
                    for idx, line in enumerate(self.banner):
                        if idx + 1 < self.height:
                            visible_part = line[:self.anim_frame]
                            for c_idx, char in enumerate(visible_part):
                                color = self.available_colors[(c_idx + self.anim_frame) % len(self.available_colors)]
                                try:
                                    self.stdscr.addch(idx + 1, 2 + c_idx, char, curses.color_pair(color) | curses.A_BOLD)
                                except curses.error: pass
                    self.anim_frame += 2
                    
                else:
                    # مرحله ۲: جریان مداوم رنگ‌ها بدون چشمک زدن و غیب شدن متن
                    for idx, line in enumerate(self.banner):
                        if idx + 1 < self.height:
                            for c_idx, char in enumerate(line):
                                color = self.available_colors[(c_idx + self.color_shift) % len(self.available_colors)]
                                try:
                                    self.stdscr.addch(idx + 1, 2 + c_idx, char, curses.color_pair(color) | curses.A_BOLD)
                                except curses.error: pass
                    self.color_shift += 1
                    
                try:
                    self.stdscr.refresh()
                except curses.error: pass
                
            except Exception: pass
            
            # سرعت حرکت افکت رنگ‌ها
            await asyncio.sleep(0.08)

# --- کلاس اصلی داشبورد اسکنر ---
class VosoghiDash:
    def __init__(self, stdscr, total_units, start_ip="-", end_ip="-"):
        self.stdscr = stdscr
        self.total = total_units
        self.scanned = 0
        self.open_count = 0
        self.active_count = 0
        self.found_list = []
        self.start_time = time.time()
        self.start_ip = start_ip
        self.end_ip = end_ip
        self.k_pressed_once = False
        
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK) 
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)    
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)     
        curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)    
        
        self.height, self.width = stdscr.getmaxyx()
        
        self.left_win = curses.newwin(max(5, self.height-12), max(10, self.width//2), 10, 1)
        self.right_win = curses.newwin(max(5, self.height-12), max(10, self.width//2 - 2), 10, max(5, self.width//2 + 1))

    def refresh_ui(self, current_target):
        elapsed = time.time() - self.start_time
        speed = self.scanned / elapsed if elapsed > 0 else 0
        pct = (self.scanned / self.total) * 100 if self.total > 0 else 0
        
        try:
            self.left_win.erase()
            self.left_win.addstr(1, 1, "==== INFORMATION ====", curses.color_pair(4) | curses.A_BOLD)
            self.left_win.addstr(3, 1, f"Start IP: {self.start_ip}", curses.color_pair(4))
            self.left_win.addstr(4, 1, f"End IP:   {self.end_ip}", curses.color_pair(4))
            self.left_win.addstr(6, 1, f"Progress: {pct:.2f}%", curses.A_BOLD)
            self.left_win.addstr(7, 1, f"Target: {current_target}") 
            self.left_win.addstr(9, 1, f"Open IP: {self.open_count}", curses.color_pair(2))
            self.left_win.addstr(10, 1, f"Active IP: {self.active_count}", curses.color_pair(1))
            self.left_win.addstr(12, 1, f"Speed: {speed:.1f} i/s", curses.color_pair(4))
            
            h_left, w_left = self.left_win.getmaxyx()
            if h_left > 3:
                self.left_win.addstr(h_left-2, 1, "Press 'k' twice to EXIT", curses.color_pair(5))
            self.left_win.box()
            self.left_win.refresh()
        except curses.error: pass

        try:
            self.right_win.erase()
            self.right_win.addstr(1, 1, "★ ACTIVE LIST ★", curses.color_pair(1) | curses.A_BOLD)
            h_right, w_right = self.right_win.getmaxyx()
            for i, item in enumerate(self.found_list[-(h_right-4):]):
                if 3 + i < h_right - 1:
                    self.right_win.addstr(3 + i, 1, f"✔ {item}", curses.color_pair(1))
            self.right_win.box()
            self.right_win.refresh()
        except curses.error: pass

def alert_user():
    os.system("termux-vibrate -d 150 &")
    os.system('termux-tts-speak -r 0.6 -p 0.05 "ali ali  ok ali ok"')

async def validate_ip(ip_str, port, dash, timeout_val):
    target = f"{ip_str}:{port}"
    try:
        connector = ProxyConnector.from_url(f"socks5://{target}")
        async with ClientSession(connector=connector, timeout=ClientTimeout(total=timeout_val)) as sess:
            async with sess.get('https://www.google.com/generate_204', ssl=False) as resp:
                if resp.status < 400:
                    dash.active_count += 1
                    dash.found_list.append(target)
                    with open("activeip.txt", "a") as f:
                        f.write(f"{target}\n")
                    alert_user()
    except: pass

async def check_target(ip, port, dash, timeout_val):
    ip_str = str(ip)
    target = f"{ip_str}:{port}"
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    try:
        sock.setsockopt(socket.IPPROTO_TCP, 1, 1)
        await asyncio.wait_for(asyncio.get_event_loop().sock_connect(sock, (ip_str, port)), timeout=float(timeout_val))
        dash.open_count += 1
        with open("openip.txt", "a") as f:
            f.write(f"{target}\n")
        asyncio.create_task(validate_ip(ip_str, port, dash, timeout_val))
    except: pass
    finally:
        sock.close()
        dash.scanned += 1
        if dash.scanned % 3 == 0: 
            dash.refresh_ui(target)

async def worker(queue, dash, timeout_val):
    while True:
        try:
            ip, port = await queue.get()
            await check_target(ip, port, dash, timeout_val)
        except asyncio.CancelledError:
            break
        finally:
            queue.task_done()

async def check_keyboard(dash):
    dash.stdscr.nodelay(True)
    while True:
        key = dash.stdscr.getch()
        if key in [ord('k'), ord('K')]:
            if dash.k_pressed_once:
                try:
                    curses.nocbreak()
                    dash.stdscr.keypad(False)
                    curses.echo()
                    curses.curs_set(1)
                    curses.endwin()
                except: pass
                print("\n[!] Scan forcefully halted by user.")
                os._exit(0)
            else:
                dash.k_pressed_once = True
                asyncio.create_task(reset_k_flag(dash))
        await asyncio.sleep(0.05)

async def reset_k_flag(dash):
    await asyncio.sleep(1.5)
    dash.k_pressed_once = False

async def run_scanner(stdscr, ips, port_list, sem_val, timeout_val):
    curses.start_color()
    curses.curs_set(0) 
    stdscr.clear()
    stdscr.refresh()
    
    start_ip = str(ips[0]) if ips else "-"
    end_ip = str(ips[-1]) if ips else "-"
    
    total_tasks = len(ips) * len(port_list)
    dash = VosoghiDash(stdscr, total_tasks, start_ip, end_ip)
    
    animator = BannerAnimator(stdscr)
    banner_task = asyncio.create_task(animator.start_loop())
    
    queue = asyncio.Queue()
    for port in port_list: 
        for ip in ips:
            queue.put_nowait((ip, port))
            
    keyboard_task = asyncio.create_task(check_keyboard(dash))
    
    workers = []
    for _ in range(sem_val):
        workers.append(asyncio.create_task(worker(queue, dash, timeout_val)))
        
    await queue.join()
    
    # === لغو تسک‌ها و آزادسازی پایدار کیبورد در ترموکس ===
    keyboard_task.cancel()
    banner_task.cancel()
    for w in workers:
        w.cancel()
    
    await asyncio.sleep(0.2)
    
    stdscr.nodelay(False) 
    curses.flushinp()  
    
    dash.refresh_ui("DONE")
    os.system('termux-tts-speak -r 0.6 -p 0.03 "finish"')
    
    try:
        stdscr.addstr(dash.height - 1, 2, " SCAN FINISHED. PRESS ANY KEY TO EXIT... ", curses.color_pair(1) | curses.A_REVERSE)
        stdscr.refresh()
    except curses.error: pass
    
    stdscr.getch()

if __name__ == "__main__":
    print("\n=== VOSOGHI SCANNER v8.0 ===")
    raw_range = input("Range (e.g., 188.114.96.0/20): ").strip()
    raw_ports = input("Ports (e.g., 1080,2080,10808,10809): ").strip()
    
    raw_sem = input("Semaphore / Concurrency [Default: 300]: ").strip()
    raw_timeout = input("Timeout in seconds [Default: 5]: ").strip()
    
    # پردازش پورت‌ها
    clean_input = "".join(c for c in raw_ports if c.isdigit() or c == ',').strip()
    DEFAULT_PORTS = [1080, 2080, 10808, 10809]
    if not clean_input:
        port_list = DEFAULT_PORTS
    else:
        try:
            port_list = [int(p) for p in clean_input.split(',') if p.strip()]
            if not port_list: port_list = DEFAULT_PORTS
        except:
            port_list = DEFAULT_PORTS

    # پردازش مقدار Sem
    if not raw_sem:
        sem_val = 300
    else:
        try:
            sem_val = int(raw_sem)
            if sem_val <= 0: sem_val = 300
        except:
            sem_val = 300

    # پردازش مقدار Timeout
    if not raw_timeout:
        timeout_val = 5.0
    else:
        try:
            timeout_val = float(raw_timeout)
            if timeout_val <= 0: timeout_val = 5.0
        except:
            timeout_val = 5.0

    # پردازش رنج آی‌پی
    try:
        network = ipaddress.ip_network(raw_range, strict=False)
        ips = list(network.hosts())
    except Exception as e:
        print(f"[!] Invalid IP Subnet Range: {e}")
        sys.exit(1)
        
    try:
        asyncio.run(curses.wrapper(run_scanner, ips, port_list, sem_val, timeout_val))
    except KeyboardInterrupt: 
        print("\n[!] Exiting...")
    finally:
        try:
            curses.nocbreak()
            curses.echo()
            curses.curs_set(1)
            curses.endwin()
        except: pass

