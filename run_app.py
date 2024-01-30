import os

import tkinter as tk
from tkinter import Label, Entry, Button

from PIL import Image, ImageTk
from dotenv import load_dotenv
from cryptography.fernet import Fernet

from App_Files.work_timer import TimerApp
from DataBase.db_reg_log import register_user, login_user
from Settings.save_settings import pre_start_configuration


def load_key():
    load_dotenv(dotenv_path="Settings/Env_Settings/.env")
    key = os.getenv('SECRET_KEY')
    if not key:
        raise Exception("No SECRET_KEY set")
    return key.encode()


cipher_suite = Fernet(load_key())
USER_DATA_FILE = 'cash_user.bin'


def encrypt_and_save_user_data(username, lastname, email, user_password):
    data = f"{username}||{lastname}||{email}||{user_password}"
    encrypted_data = cipher_suite.encrypt(data.encode())
    with open(USER_DATA_FILE, 'wb') as file:
        file.write(encrypted_data)


def load_and_decrypt_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'rb') as file:
            encrypted_data = file.read()
            decrypted_data = cipher_suite.decrypt(encrypted_data).decode()

            username, lastname, email, password = decrypted_data.split("||")

            return username, lastname, email, password

    return None, None, None, None


def image_con(image_path_root, x, y):
    image_path = os.path.dirname(os.path.abspath(__file__))
    big_image_path = image_path + image_path_root
    image_path = os.path.join(big_image_path)
    bg_image = Image.open(image_path)
    bg_image = bg_image.resize((x, y))
    bg_photo = ImageTk.PhotoImage(bg_image)
    return bg_photo


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Timer App")
        self.root.geometry("300x500")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=300, height=500)
        self.canvas.pack(fill="both", expand=True)

        self.frame = tk.Frame(self.root)
        # self.frame.place(x=100, y=0, width=400, height=400)

        self.first_name_label = Label(self.canvas, text="First Name")
        self.first_name_entry = Entry(self.canvas)
        self.last_name_label = Label(self.canvas, text="Last Name")
        self.last_name_entry = Entry(self.canvas)

        self.email_label = Label(self.canvas, text="Email")
        self.email_entry = Entry(self.canvas)
        self.password_label = Label(self.canvas, text="Password")
        self.password_entry = Entry(self.canvas, show='*')
        self.submit_button = Button(self.canvas, text="Submit", command=self.submit_form)

        self.toggle_button = Button(self.canvas, text="Switch to Login", command=self.toggle_form)

        self.is_registration_form = True
        self.update_form_view()

        username, lastname, email, password = load_and_decrypt_user_data()

        if username and lastname and email and password:
            self.create_main_interface(username, lastname, email, password)

    def toggle_form(self):
        self.is_registration_form = not self.is_registration_form
        self.update_form_view()

    def update_form_view(self):
        for widget in self.canvas.winfo_children():
            widget.pack_forget()

        if self.is_registration_form:
            y = 50
            self.first_name_label.place(x=140, y=y)
            self.first_name_entry.place(x=140, y=y + 20)
            self.last_name_label.place(x=140, y=y + 40)
            self.last_name_entry.place(x=140, y=y + 60)
            self.email_label.place(x=140, y=y + 80)
            self.email_entry.place(x=140, y=y + 100)
            self.password_label.place(x=140, y=y + 120)
            self.password_entry.place(x=140, y=y + 140)
            self.submit_button.place(x=140, y=y + 160)
            self.toggle_button.config(text="Switch to Login")
            self.change_canvas_background("\\App_image\\bg_reg.png")

        else:
            self.email_label.pack()
            self.email_entry.pack()
            self.password_label.pack()
            self.password_entry.pack()
            self.submit_button.pack()
            self.change_canvas_background("\\App_image\\bg_log.png")
            # image_con("\\App_image\\bg_log.png")
            self.toggle_button.config(text="Switch to Register")

        self.toggle_button.place(x=70, y=30)

    def create_main_interface(self, username, lastname, email, password):
        self.root.destroy()

        app_root = tk.Tk()
        TimerApp(app_root, username, lastname, email)

    def submit_form(self):
        email = self.email_entry.get()
        username = self.first_name_entry.get()
        password = self.password_entry.get()

        if self.is_registration_form:
            first_name = self.first_name_entry.get()
            last_name = self.last_name_entry.get()
            if register_user(email, first_name, last_name, password):
                print("Registering:", first_name, last_name, email, password)
                encrypt_and_save_user_data(username, last_name, email, password)
                self.create_main_interface(username, last_name, email, password)
        else:
            login_bool, username, last_name = login_user(email, password)
            if login_bool:
                encrypt_and_save_user_data(username, last_name, email, password)
                self.create_main_interface(username, last_name, email, password)
                print("Login successful")
            else:
                print("Wrong email or password")

    def change_canvas_background(self, new_bg_path):
        new_bg_photo = image_con(new_bg_path, 300, 500)
        self.canvas.create_image(0, 0, anchor="nw", image=new_bg_photo)
        self.canvas.image = new_bg_photo


if __name__ == "__main__":
    try:
        pre_start_configuration()
        root = tk.Tk()
        app = App(root)

        root.mainloop()
    except Exception as e:
        print(e)
