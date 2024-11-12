import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import tkinter as tk
import customtkinter as ctk
import subprocess
import threading

# Configure CustomTkinter
ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

# OTP and email setup
generated_otp = None
email_address = "your-email@gmail.com"  # replace with your Gmail account
email_password = "your-password"  # replace with your Gmail password

# Function to generate OTP
def generate_otp():
    global generated_otp
    generated_otp = ''.join(random.choices("0123456789", k=6))
    return generated_otp

# Function to send OTP email
def send_otp_email(receiver_email):
    otp = generate_otp()
    msg = MIMEMultipart()
    msg["From"] = email_address
    msg["To"] = receiver_email
    msg["Subject"] = "Your OTP for Camera Access"
    message = f"<h1>Your OTP is {otp}</h1>"
    msg.attach(MIMEText(message, "html"))
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email_address, email_password)
        server.sendmail(email_address, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

# Camera control functions using PowerShell
def disable_camera():
    subprocess.run("powershell Disable-PnpDevice -InstanceId 'CameraInstanceID' -Confirm:$false", shell=True)

def enable_camera():
    subprocess.run("powershell Enable-PnpDevice -InstanceId 'CameraInstanceID' -Confirm:$false", shell=True)

def check_camera_status():
    status = subprocess.run("powershell Get-PnpDevice -FriendlyName 'CameraDeviceName' | Select-Object Status", shell=True, capture_output=True, text=True)
    return "Disabled" in status.stdout

# GUI setup
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Camera Controller with OTP Authentication")
        self.geometry("400x400")

        # Email entry
        self.email_label = ctk.CTkLabel(self, text="Enter Email:")
        self.email_label.pack(pady=10)
        self.email_entry = ctk.CTkEntry(self)
        self.email_entry.pack(pady=10)
        
        # OTP entry
        self.otp_label = ctk.CTkLabel(self, text="Enter OTP:")
        self.otp_label.pack(pady=10)
        self.otp_entry = ctk.CTkEntry(self)
        self.otp_entry.pack(pady=10)

        # OTP button
        self.send_otp_button = ctk.CTkButton(self, text="Send OTP", command=self.send_otp)
        self.send_otp_button.pack(pady=10)

        # Verify button
        self.verify_button = ctk.CTkButton(self, text="Verify OTP", command=self.verify_otp)
        self.verify_button.pack(pady=10)

        # Camera control buttons
        self.disable_button = ctk.CTkButton(self, text="Disable Camera", command=disable_camera, state="disabled")
        self.disable_button.pack(pady=10)

        self.enable_button = ctk.CTkButton(self, text="Enable Camera", command=enable_camera, state="disabled")
        self.enable_button.pack(pady=10)

        self.status_button = ctk.CTkButton(self, text="Check Camera Status", command=self.check_status, state="disabled")
        self.status_button.pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text="Camera Status: Unknown")
        self.status_label.pack(pady=10)

    # Send OTP function
    def send_otp(self):
        receiver_email = self.email_entry.get()
        threading.Thread(target=send_otp_email, args=(receiver_email,)).start()
    
    # Verify OTP function
    def verify_otp(self):
        user_otp = self.otp_entry.get()
        if user_otp == generated_otp:
            self.disable_button.configure(state="normal")
            self.enable_button.configure(state="normal")
            self.status_button.configure(state="normal")
            self.status_label.configure(text="OTP Verified! Camera controls unlocked.")
        else:
            self.status_label.configure(text="Invalid OTP. Please try again.")

    # Check camera status function
    def check_status(self):
        camera_status = "Enabled" if not check_camera_status() else "Disabled"
        self.status_label.configure(text=f"Camera Status: {camera_status}")

# Run the app
if __name__ == "__main__":
    app = App()
    app.mainloop()
