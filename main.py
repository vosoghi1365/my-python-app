import asyncio
import ipaddress
import socket
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from aiohttp import ClientSession, ClientTimeout
from aiohttp_socks import ProxyConnector
class ScannerDashboard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=15, spacing=10, **kwargs)
        self.add_widget(Label(
            text="[b]VOSOGHI SCANNER v8.0[/b]", 
            markup=True, 
            font_size='22sp', 
            size_hint_y=None, 
            height=40,
            color=get_color_from_hex("#00FFCC")
        ))
         # فیلدهای ورودی
        self.add_widget(Label(text="IP Range (e.g., 188.114.96.0/24):", size_hint_y=None, height=25, halign='left'))
        self.ip_input = TextInput(text="188.114.96.0/24", multiline=False, size_hint_y=None, height=40)
        self.add_widget(self.ip_input)
        self.add_widget(Label(text="Ports (comma separated):", size_hint_y=None, height=25))
        self.port_input = TextInput(text="1080, 2080, 10808", multiline=False, size_hint_y=None, height=40)
        self.add_widget(self.port_input)
                # دکمه شروع
        self.start_btn = Button(
            text="START SCAN", 
            font_size='18sp', 
            bold=True,
            background_color=get_color_from_hex("#00AA55"),
            size_hint_y=None, 
            height=50
        )
        self.start_btn.bind(on_press=self.start_scan)
        self.add_widget(self.start_btn)
        # نمایش نتایج (کنسول خروجی)
        self.scroll = ScrollView(bar_width=10)
        self.log_label = Label(
            text="Ready to scan...\n", 
            size_hint_y=None, 
            halign='left', 
            valign='top',
            font_name='Roboto',
            font_size='14sp'
        )
        self.log_label.bind(texture_size=self.log_label.setter('size'))
        self.scroll.add_widget(self.log_label)
        self.add_widget(self.scroll)
        self.is_scanning = False
    def start_scan(self, instance):
        if self.is_scanning:
            return
        self.is_scanning = True
        self.start_btn.disabled = True
        self.start_btn.text = "SCANNING..."
        self.log_label.text = "[*] Initializing network scanner...\n"
            # راه‌اندازی لوپ ناهمگام در کلاک کیوی
        loop = asyncio.get_event_loop()
        loop.create_task(self.run_network_scan())
    async def run_network_scan(self):
        raw_range = self.ip_input.text.strip()
        raw_ports = self.port_input.text.strip()
       try:
            network = ipaddress.ip_network(raw_range, strict=False)
            ports = [int(p.strip()) for p in raw_ports.split(',') if p.strip()]
        except Exception as e:
            self.update_log(f"[-] Input Error: {str(e)}\n")
            self.reset_button()
            return
        self.update_log(f"[*] Total hosts to scan: {len(list(network.hosts()))}\n")
        for ip in network.hosts():
            for port in ports:
                target_ip = str(ip)
                self.update_log(f"[🔍] Checking {target_ip}:{port}...\n")
                # منطق اسکن سوکت کانکشن ناهمگام
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setblocking(False)
                try:
                    await asyncio.wait_for(
                        asyncio.get_event_loop().sock_connect(sock, (target_ip, port)), 
                        timeout=3.0
                    )
                    self.update_log(f"[✅] OPEN PORT FOUND: {target_ip}:{port}\n")
                except:
                    pass
                finally:
                    sock.close()
                await asyncio.sleep(0.01) # برای اینکه رابط کاربری موبایل قفل نکند
        self.update_log("\n[🏁] Scan completed successfully.")
        self.reset_button()
    def update_log(self, text):
        self.log_label.text += text
    def reset_button(self):
        self.is_scanning = False
        self.start_btn.disabled = False
        self.start_btn.text = "START SCAN"
class VosoghiScannerApp(App):
    def build(self):
        # هماهنگ‌سازی حلقه asyncio با فریم‌ورک اصلی اندروید
        loop = asyncio.get_event_loop()
        Clock.schedule_interval(lambda dt: loop.stop() or loop.run_until_complete(asyncio.sleep(0)), 0.05)
        return ScannerDashboard()
if __name__ == "__main__":
    VosoghiScannerApp().run()
