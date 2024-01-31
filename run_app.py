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
        self.root.geometry("400x570")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=400, height=570)
        self.canvas.pack(fill="both", expand=True)

        self.first_name_label = Label(self.canvas, text="First Name", font=("Helvetica", 12), background="#a6a6a6")
        self.first_name_entry = Entry(self.canvas, borderwidth=0, highlightthickness=0)
        self.last_name_label = Label(self.canvas, text="Last Name", font=("Helvetica", 12), background="#a6a6a6")
        self.last_name_entry = Entry(self.canvas)

        self.email_label = Label(self.canvas, text="Email", font=("Helvetica", 12), background="#a6a6a6")
        self.email_entry = Entry(self.canvas)
        self.password_label = Label(self.canvas, text="Password", font=("Helvetica", 12), background="#a6a6a6")
        self.password_entry = Entry(self.canvas, show='*')
        self.submit_button = Button(self.canvas, text="Submit", command=self.submit_form, background="#a6a6a6",
                                    borderwidth=0, highlightthickness=0, font=("Helvetica", 11, "bold"), width=10,
                                    height=1)

        self.enter_button = os.path.dirname(os.path.abspath(__file__)) + "\\App_image\\enter_button.png"
        self.enter_button_1 = Image.open(self.enter_button).resize(
            (100, 40))
        self.enter_button_2 = ImageTk.PhotoImage(self.enter_button_1)
        self.toggle_button = Button(self.canvas, text="Switch to Login", command=self.toggle_form, background="#a6a6a6",
                                    borderwidth=0, highlightthickness=0, font=("Helvetica", 11, "bold"))

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
            y = 134
            self.first_name_label.place(x=135, y=y)
            self.first_name_entry.place(x=95, y=y + 27)
            self.last_name_label.place(x=140, y=y + 89)
            self.last_name_entry.place(x=95, y=y + 116)
            self.email_label.place(x=160, y=y + 178)
            self.email_entry.place(x=95, y=y + 205)
            self.password_label.place(x=140, y=y + 268)
            self.password_entry.place(x=95, y=y + 295)
            self.submit_button.place(x=130, y=y + 365)
            self.toggle_button.config(text="Switch to Login")

            self.email_entry.delete(0, tk.END)
            self.first_name_entry.delete(0, tk.END)
            self.last_name_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)

            self.first_name_label.config(background="#a6a6a6")
            self.last_name_label.config(background="#a6a6a6")
            self.email_label.config(background="#a6a6a6")
            self.password_label.config(background="#a6a6a6")

            self.change_canvas_background("\\App_image\\bg_reg.png")
            self.status = "registration"

            self.toggle_button.place(x=113, y=36)

        else:
            # hide element
            self.first_name_label.place_forget()
            self.first_name_entry.place_forget()
            self.last_name_label.place_forget()
            self.last_name_entry.place_forget()

            self.email_label.place(x=162, y=160)
            self.email_entry.place(x=97, y=200)
            self.password_label.place(x=140, y=310)
            self.password_entry.place(x=97, y=350)
            self.submit_button.place(x=130, y=499)

            self.first_name_label.config(background="#a6a6a6")
            self.last_name_label.config(background="#a6a6a6")
            self.email_label.config(background="#a6a6a6")
            self.password_label.config(background="#a6a6a6")

            self.change_canvas_background("\\App_image\\bg_log.png")
            self.toggle_button.config(text="Switch to\n Registration")
            self.status = "login"

            self.toggle_button.place(x=130, y=35)

    def create_main_interface(self, username, lastname, email, password):
        self.root.destroy()

        app_root = tk.Tk()
        TimerApp(app_root, username, lastname, email)

    def check_enter(self, email, password, username):
        if email == "" or email == "Email already exists":
            self.email_label.config(background="red")
        else:
            self.email_label.config(background="#a6a6a6")
        if password == "":
            self.password_label.config(background="red")
        else:
            self.password_label.config(background="#a6a6a6")
        if username == "":
            self.first_name_label.config(background="red")
        else:
            self.first_name_label.config(background="#a6a6a6")

    def password_and_email_check(self, email, password):
        print("check")
        # if gmail dont have @
        if "@" not in email:
            self.email_label.config(background="red")
            self.email_entry.delete(0, tk.END)
            self.email_entry.insert(0, "Wrong email!")
            return False
        # Check if password is correct
        if " " in password:
            self.password_label.config(background="red")
            self.password_entry.delete(0, tk.END)
            return False
        return True

    def submit_form(self):
        email = self.email_entry.get()
        username = self.first_name_entry.get()
        password = self.password_entry.get()
        if (email == "" or password == "" or username == "" or email == "Email already exists") \
                and self.status == "registration":

            self.check_enter(email, password, username)
        else:
            self.check_enter(email, password, username)
            if self.is_registration_form:
                if self.password_and_email_check(email, password):
                    first_name = self.first_name_entry.get()
                    last_name = self.last_name_entry.get()
                    if register_user(email, first_name, last_name, password):
                        print("Registering:", first_name, last_name, email, password)
                        encrypt_and_save_user_data(username, last_name, email, password)
                        self.create_main_interface(username, last_name, email, password)
                    else:
                        self.email_label.config(background="red")
                        self.email_entry.delete(0, tk.END)
                        self.first_name_entry.delete(0, tk.END)
                        self.last_name_entry.delete(0, tk.END)
                        self.password_entry.delete(0, tk.END)
                        self.email_entry.insert(0, "Email already exists")

            else:
                login_bool, username, last_name = login_user(email, password)

                if login_bool:
                    encrypt_and_save_user_data(username, last_name, email, password)
                    self.create_main_interface(username, last_name, email, password)
                    print("Login successful")
                else:
                    self.email_label.config(background="red")
                    self.password_label.config(background="red")
                    self.email_entry.delete(0, tk.END)
                    self.password_entry.delete(0, tk.END)
                    self.email_entry.insert(0, "Wrong email or password!")

    def change_canvas_background(self, new_bg_path):
        new_bg_photo = image_con(new_bg_path, 400, 570)
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
