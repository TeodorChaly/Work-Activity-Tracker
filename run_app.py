import os
import time

import tkinter as tk
from tkinter import Label, Entry, Button
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


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Timer App")

        self.frame = tk.Frame(self.root)
        self.frame.pack()

        self.first_name_label = Label(self.frame, text="First Name")
        self.first_name_entry = Entry(self.frame)
        self.last_name_label = Label(self.frame, text="Last Name")
        self.last_name_entry = Entry(self.frame)

        self.email_label = Label(self.frame, text="Email")
        self.email_entry = Entry(self.frame)
        self.password_label = Label(self.frame, text="Password")
        self.password_entry = Entry(self.frame, show='*')
        self.submit_button = Button(self.frame, text="Submit", command=self.submit_form)

        self.toggle_button = Button(self.frame, text="Switch to Login", command=self.toggle_form)

        self.is_registration_form = True
        self.update_form_view()
        username, lastname, email, password = load_and_decrypt_user_data()
        if username and lastname and email and password:
            self.create_main_interface(username, lastname, email, password)

    def toggle_form(self):
        self.is_registration_form = not self.is_registration_form
        self.update_form_view()

    def update_form_view(self):
        for widget in self.frame.winfo_children():
            widget.pack_forget()

        if self.is_registration_form:
            self.first_name_label.pack()
            self.first_name_entry.pack()
            self.last_name_label.pack()
            self.last_name_entry.pack()
            self.email_label.pack()
            self.email_entry.pack()
            self.password_label.pack()
            self.password_entry.pack()
            self.submit_button.pack()
            self.toggle_button.config(text="Switch to Login")
        else:
            self.email_label.pack()
            self.email_entry.pack()
            self.password_label.pack()
            self.password_entry.pack()
            self.submit_button.pack()
            self.toggle_button.config(text="Switch to Register")

        self.toggle_button.pack()

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
                # encrypt_and_save_user_data(username, last_name, email, password)
                # self.create_main_interface(username, last_name, email, password)
                print("Login successful")
                pass  # Take from DB
            else:
                print("Wrong email or password")


if __name__ == "__main__":
    try:
        pre_start_configuration()
        root = tk.Tk()
        app = App(root)
        root.mainloop()
    except Exception as e:
        time.sleep(10)
        print(e)
