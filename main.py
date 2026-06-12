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

class ScannerWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)
        
        # بخش ورودی‌ها
        self.add_widget(Label(text="VOSOGHI SCANNER v8.0 (Mobile Edition)", font_size=20, bold=True))
        
        self.ip_input = TextInput(text="188.114.96.0/20", hint_text="Subnet Range", multiline=False)
        self.add_widget(self.ip_input)
        
        self.port_input = TextInput(text="1080,2080", hint_text="Ports", multiline=False)
        self.add_widget(self.port_input)
        
        self.start_btn = Button(text="START SCAN", background_color=(0, 1, 0, 1))
        self.start_btn.bind(on_press=self.start_scan)
        self.add_widget(self.start_btn)
        
        # نمایش نتایج
        self.scroll = ScrollView()
        self.log_label = Label(text="Results will appear here...\n", size_hint_y=None, halign='left')
        self.log_label.bind(texture_size=self.log_label.setter('size'))
        self.scroll.add_widget(self.log_label)
        self.add_widget(self.scroll)

    def start_scan(self, instance):
        self.log_label.text = "Initializing Scanner...\n"
        # اجرای چرخه Asyncio در پشت صحنه کیوی برای جلوگیری از فریز شدن برنامه
        loop = asyncio.get_event_loop()
        loop.create_task(self.run_async_scan())

    async def run_async_scan(self):
        try:
            network = ipaddress.ip_network(self.ip_input.text.strip(), strict=False)
            ports = [int(p) for p in self.port_input.text.split(',')]
            
            for ip in network.hosts():
                for port in ports:
                    self.log_label.text += f"Checking {ip}:{port}...\n"
                    await asyncio.sleep(0.01) # شبیه‌سازی اسکن ناهمگام
        except Exception as e:
            self.log_label.text += f"Error: {e}\n"

class VosoghiScannerApp(App):
    def build(self):
        # تنظیم کلاک اصلی برای اجرای همزمان فریم‌ورک کامپایل اندروید با Asyncio
        loop = asyncio.get_event_loop()
        Clock.schedule_interval(lambda dt: loop.stop() or loop.run_until_complete(asyncio.sleep(0)), 0.03)
        return ScannerWidget()

if __name__ == "__main__":
    VosoghiScannerApp().run()
