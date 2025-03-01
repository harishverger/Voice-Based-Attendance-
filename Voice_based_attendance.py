import mysql.connector
import speech_recognition as sr
from datetime import datetime
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager

# KivyMD UI Design (Fixed Navigation)
KV = """
MDScreenManager:
    LoginScreen:
    MainScreen:
    AttendanceScreen:
    
<LoginScreen>:
    name: "login"
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(10)
        padding: dp(20)

        MDLabel:
            text: "Login"
            font_style: "H4"
            halign: "center"
            theme_text_color: "Primary"

        MDTextField:
            id: username
            hint_text: "Username"
            mode: "rectangle"
            icon_right: "account"
            pos_hint: {"center_x": 0.5}
            size_hint_x: 0.8

        MDTextField:
            id: password
            hint_text: "Password"
            mode: "rectangle"
            password: True
            icon_right: "lock"
            pos_hint: {"center_x": 0.5}
            size_hint_x: 0.8

        MDRaisedButton:
            text: "Login"
            pos_hint: {"center_x": 0.5}
            on_release: app.check_login()

        MDLabel:
            id: login_status
            text: ""
            halign: "center"
            theme_text_color: "Error"

<MainScreen>:
    name: "main"
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(10)
        padding: dp(20)

        MDLabel:
            text: "Voice-Based Attendance System"
            font_style: "H5"
            halign: "center"
            theme_text_color: "Primary"

        MDRaisedButton:
            text: "Record Attendance"
            pos_hint: {"center_x": 0.5}
            on_release: app.listen_for_name()

        MDLabel:
            id: status
            text: "Press the button and speak your name"
            halign: "center"
            theme_text_color: "Secondary"

        MDRaisedButton:
            text: "View Attendance"
            pos_hint: {"center_x": 0.5}
            on_release: app.show_attendance()

        MDRaisedButton:
            text: "Exit"
            pos_hint: {"center_x": 0.5}
            md_bg_color: 1, 0, 0, 1
            on_release: app.stop()

<AttendanceScreen>:
    name: "attendance"
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(10)
        padding: dp(20)

        MDLabel:
            text: "Attendance Records"
            font_style: "H5"
            halign: "center"
            theme_text_color: "Primary"

        MDScrollView:
            MDBoxLayout:
                id: attendance_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height

        MDRaisedButton:
            text: "Back"
            pos_hint: {"center_x": 0.5}
            on_release: app.go_back()
"""

class LoginScreen(MDScreen):
    pass

class MainScreen(MDScreen):
    pass

class AttendanceScreen(MDScreen):
    pass

class VoiceAttendanceApp(MDApp):

    def check_login(self):
        username = self.root.get_screen('login').ids.username.text.strip()
        password = self.root.get_screen('login').ids.password.text.strip()

        if not username or not password:
            self.show_dialog("Error", "Please enter both username and password.")
            self.root.get_screen('login').ids.username.text = ''
            self.root.get_screen('login').ids.password.text = ''
            return

        if not self.connection or not self.cursor:
            self.show_dialog("Error", "Database connection error.")
            self.root.get_screen('login').ids.username.text = ''
            self.root.get_screen('login').ids.password.text = ''
            return

        try:
            sql = "SELECT * FROM login WHERE username = %s AND password = %s"
            self.cursor.execute(sql, (username, password))
            user = self.cursor.fetchone()

            if user:
                self.root.current = "main"
            else:
                self.show_dialog("Error", "Invalid username or password.")
                self.root.get_screen('login').ids.username.text = ''
                self.root.get_screen('login').ids.password.text = ''
        except mysql.connector.Error as err:
            self.show_dialog("Error", f"Database error: {str(err)}")
            self.root.get_screen('login').ids.username.text = ''
            self.root.get_screen('login').ids.password.text = ''

    def show_dialog(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            size_hint=(0.8, 0.3)
        )
        dialog.open()

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        self.connection = None
        self.cursor = None
        self.connect_to_db()

        return Builder.load_string(KV)

    def connect_to_db(self):
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='ASdf@2004', 
                database='internship_project',
                autocommit=True
            )
            self.cursor = self.connection.cursor()
        except mysql.connector.Error as err:
            print(f"Database connection error: {err}")
            self.connection = None
            self.cursor = None

    def record_attendance(self, name):
        if not self.connection or not self.cursor:
            self.root.get_screen('main').ids.status.text = "Database connection error."
            return

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        try:
            sql = "INSERT INTO attendance (name, date, time) VALUES (%s, %s, %s)"
            values = (name, date_str, time_str)
            self.cursor.execute(sql, values)
            self.root.get_screen('main').ids.status.text = f"Attendance for {name} recorded successfully!"
        except mysql.connector.Error as err:
            self.root.get_screen('main').ids.status.text = "Database error: " + str(err)

    def listen_for_name(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.root.get_screen('main').ids.status.text = "Listening..."
            try:
                audio = recognizer.listen(source, timeout=5)
                name = recognizer.recognize_google(audio).strip().title()
                if name:
                    self.record_attendance(name)
                else:
                    self.root.get_screen('main').ids.status.text = "No name detected. Try again."
            except sr.UnknownValueError:
                self.root.get_screen('main').ids.status.text = "Could not understand the audio. Try again."
            except sr.RequestError:
                self.root.get_screen('main').ids.status.text = "Check your internet connection."
            except Exception as e:
                self.root.get_screen('main').ids.status.text = f"Error: {str(e)}"

    def show_attendance(self):
        self.root.current = "attendance"
        self.load_attendance()

    def go_back(self):
        self.root.current = "main"

    def load_attendance(self):
        if not self.connection or not self.cursor:
            self.root.get_screen('attendance').ids.attendance_list.clear_widgets()
            self.root.get_screen('attendance').ids.attendance_list.add_widget(MDLabel(text="Database connection error.", halign="center"))
            return

        try:
            self.cursor.execute("SELECT name, date, time FROM attendance ORDER BY date DESC, time DESC")
            records = self.cursor.fetchall()

            attendance_list = self.root.get_screen('attendance').ids.attendance_list
            attendance_list.clear_widgets()

            if not records:
                attendance_list.add_widget(MDLabel(text="No attendance records found.", halign="center"))
            else:
                for name, date, time in records:
                    label = MDLabel(
                        text=f"{name} - {date} {time}",
                        theme_text_color="Primary",
                        font_style="Body1",
                        size_hint_y=None  
                    )
                    attendance_list.add_widget(label)
        except mysql.connector.Error as err:
            self.root.get_screen('attendance').ids.attendance_list.add_widget(MDLabel(text=f"Error loading records: {str(err)}", halign="center"))

    def on_stop(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

if __name__ == '__main__':
    VoiceAttendanceApp().run()
