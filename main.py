import os
import sys
#KivyMD的字体自动加载
os.environ['KIVY_NO_FONTCONFIG'] = '1'

from kivy.config import Config
Config.set('kivy', 'default_font', ['Roboto', 'Roboto-Regular.ttc'])

from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDFillRoundFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.label import MDLabel
from kivy.core.text import LabelBase

# 1. 解决中文字体问题 - 使用项目中的字体文件
try:
    #尝使用使用项目中的Roboto字体
    font_path = os.path.join(os.path.dirname(__file__), 'Roboto-Regular.ttc')
    if os.path.exists(font_path):
        LabelBase.register(name='Roboto', fn_regular=font_path)
        LabelBase.register(name='Chinese', fn_regular=font_path)
    else:
        #备方案
        font_path = os.path.join(os.path.dirname(__file__), 'fake_fonts', 'Roboto-Regular.ttc')
        if os.path.exists(font_path):
            LabelBase.register(name='Roboto', fn_regular=font_path)
            LabelBase.register(name='Chinese', fn_regular=font_path)
except Exception as e:
    print(f"字体注册失败: {e}")

class ESP32ControllerApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"  # 设置主色调
        self.theme_cls.theme_style = "Light"     # 浅色模式（类似iOS）

        # 主布局：纵向排列，撑满全屏
        main_layout = MDBoxLayout(orientation='vertical', padding=20, spacing=20)

        # --- 第一栏：WiFi 和按键 (居中对齐) ---
        top_bar = MDBoxLayout(adaptive_height=True, spacing=20, padding=[0, 10], 
                             size_hint_y=None, height=60)
        
        #左弹性空间
        top_bar.add_widget(MDBoxLayout(size_hint_x=0.1))
        
        # WiFi按钮 - 绿色主题
        btn_wifi = MDRaisedButton(
            text="● WiFi连接", 
            font_name='Chinese', 
            size_hint_x=0.35,
            md_bg_color=(0.2, 0.7, 0.3, 1)  # 绿色
        )
        btn_wifi.bind(on_release=lambda x: self.send_command("CONNECT_WIFI"))
        
        #蓝牙按钮 - 蓝色主题  
        btn_bt = MDRaisedButton(
            text="● 蓝牙连接", 
            font_name='Chinese', 
            size_hint_x=0.35,
            md_bg_color=(0.2, 0.4, 0.8, 1)  # 蓝色
        )
        btn_bt.bind(on_release=lambda x: self.send_command("CONNECT_BT"))
        
        top_bar.add_widget(btn_wifi)
        top_bar.add_widget(btn_bt)
        
        #右弹性空间
        top_bar.add_widget(MDBoxLayout(size_hint_x=0.1))
        main_layout.add_widget(top_bar)

        # --- 第二栏：WiFi和蓝牙独立开关 (苹果风格，居中对齐) ---
        switch_layout = MDBoxLayout(adaptive_height=True, padding=[20, 30], 
                                   size_hint_y=None, height=120, spacing=15)
                
        # WiFi开关组
        wifi_box = MDBoxLayout(orientation='horizontal', spacing=15, size_hint_x=0.5)
                
        #左弹性空间
        wifi_box.add_widget(MDBoxLayout(size_hint_x=0.1))
                
        wifi_label = MDLabel(
            text="WiFi开关", 
            font_name='Chinese', 
            halign="center",
            size_hint_x=0.6
        )
                
        self.wifi_switch = MDSwitch(
            width="64dp",
            size_hint_x=None
        )
        self.wifi_switch.bind(active=self.on_wifi_switch)
                
        wifi_box.add_widget(wifi_label)
        wifi_box.add_widget(self.wifi_switch)
        wifi_box.add_widget(MDBoxLayout(size_hint_x=0.1))
                
        #蓝牙开关组
        bt_box = MDBoxLayout(orientation='horizontal', spacing=15, size_hint_x=0.5)
                
        #左弹性空间
        bt_box.add_widget(MDBoxLayout(size_hint_x=0.1))
                
        bt_label = MDLabel(
            text="蓝牙开关", 
            font_name='Chinese', 
            halign="center",
            size_hint_x=0.6
        )
                
        self.bt_switch = MDSwitch(
            width="64dp",
            size_hint_x=None
        )
        self.bt_switch.bind(active=self.on_bt_switch)
                
        bt_box.add_widget(bt_label)
        bt_box.add_widget(self.bt_switch)
        bt_box.add_widget(MDBoxLayout(size_hint_x=0.1))
                
        switch_layout.add_widget(wifi_box)
        switch_layout.add_widget(bt_box)
        main_layout.add_widget(switch_layout)

        # --- 第三栏：档位选择 (占满剩余空间) ---
        gear_container = MDBoxLayout(orientation='horizontal', spacing=10)
        
        # 左侧：档位文本
        gear_label = MDLabel(
            text="档位", 
            font_name='Chinese', 
            font_style="H5",
            size_hint_x=0.3, 
            halign="center"
        )
        gear_container.add_widget(gear_label)

        # 右侧：百分比按钮组 (垂直排列)
        buttons_layout = MDBoxLayout(orientation='vertical', spacing=10, size_hint_x=0.7)
        percentages = ["20%", "40%", "60%", "80%", "100%"]
        
        for p in percentages:
            btn = MDFillRoundFlatButton(
                text=p, 
                size_hint=(1, 1), # 自动撑满垂直空间
                font_style="Button"
            )
            # 绑定点击事件，发送对应档位
            btn.bind(on_release=lambda x, val=p: self.send_command(f"GEAR_{val}"))
            buttons_layout.add_widget(btn)
        
        gear_container.add_widget(buttons_layout)
        main_layout.add_widget(gear_container)

        return main_layout

    def on_wifi_switch(self, instance, value):
        """WiFi开关状态改变"""
        if value:
            self.send_command("WIFI_ON")
            print("WiFi已开启")
        else:
            self.send_command("WIFI_OFF")
            print("WiFi已关闭")

    def on_bt_switch(self, instance, value):
        """蓝牙开关状态改变"""
        if value:
            self.send_command("BT_ON")
            print("蓝牙已开启")
        else:
            self.send_command("BT_OFF")
            print("蓝牙已关闭")

    def send_command(self, command):
        """
        这里是发送代码的逻辑
        后续你需要在这里调用蓝牙(pybluez)或WiFi(socket)的库来给ESP32传指令
        """
        print(f"[发送指令到ESP32]: {command}")

if __name__ == '__main__':
    ESP32ControllerApp().run()