import socket
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading

SERVER_IP = "72.60.39.182"
SERVER_PORT = 1923
CHECK_INTERVAL = 10
IMAGE_URL = "https://b.catgirlsare.sexy/XO5_O2BSUooJ.png"

class ServerMonitor:
    def __init__(self):
        self.monitoring = False
        self.check_thread = None
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("BYOND Server Monitor")
        self.root.geometry("300x150")
        
        # Status label
        self.status_label = tk.Label(self.root, text="Monitor: OFF", font=("Arial", 14))
        self.status_label.pack(pady=10)
        
        # Server status
        self.server_label = tk.Label(self.root, text="Server: Unknown", font=("Arial", 12))
        self.server_label.pack(pady=5)
        
        # Toggle button
        self.toggle_btn = tk.Button(self.root, text="Start Monitoring", 
                                     command=self.toggle_monitoring, 
                                     font=("Arial", 12), bg="green", fg="white")
        self.toggle_btn.pack(pady=20)
        
        self.root.mainloop()
    
    def check_server(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((SERVER_IP, SERVER_PORT))
            
            if result != 0:
                print(f"[DEBUG] Port closed, code: {result}")
                sock.close()
                return False
            
            # Port is open, now try to get server info
            # BYOND servers respond to a topic query
            try:
                # Send a simple query to verify server is responding
                sock.send(b"\x00\x83")  # BYOND handshake bytes
                sock.settimeout(2)
                response = sock.recv(1024)
                
                if len(response) > 0:
                    print(f"[DEBUG] ✅ Server responded! Got {len(response)} bytes")
                    sock.close()
                    return True
                else:
                    print("[DEBUG] ❌ No response from server")
                    sock.close()
                    return False
                    
            except socket.timeout:
                print("[DEBUG] ❌ Server didn't respond to handshake (timeout)")
                sock.close()
                return False
                
        except Exception as e:
            print(f"[DEBUG] ❌ Error: {e}")
            return False
    
    def monitor_loop(self):
        while self.monitoring:
            is_online = self.check_server()
            
            if is_online:
                self.server_label.config(text="Server: ONLINE ✅", fg="green")
                self.monitoring = False
                self.show_alert_image()
                break
            else:
                self.server_label.config(text="Server: OFFLINE ❌", fg="red")
            
            time.sleep(CHECK_INTERVAL)
    
    def show_alert_image(self):
        # Create new window with the image
        alert_window = tk.Toplevel(self.root)
        alert_window.title("Server is UP!")
        
        try:
            # Download and display image
            response = requests.get(IMAGE_URL)
            img_data = Image.open(BytesIO(response.content))
            img_data = img_data.resize((400, 400), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img_data)
            
            label = tk.Label(alert_window, image=photo, cursor="hand2")
            label.image = photo  # Keep reference
            label.pack()
            
            # Click to close
            def close_alert(event):
                alert_window.destroy()
                self.stop_monitoring()
            
            label.bind("<Button-1>", close_alert)
            
            alert_window.focus_force()
            alert_window.lift()
            
        except Exception as e:
            tk.Label(alert_window, text=f"Server is UP!\n(Error loading image: {e})", 
                    font=("Arial", 14)).pack(pady=20)
            tk.Button(alert_window, text="Close", command=lambda: [alert_window.destroy(), self.stop_monitoring()]).pack()
    
    def toggle_monitoring(self):
        if self.monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()
    
    def start_monitoring(self):
        self.monitoring = True
        self.status_label.config(text="Monitor: ON", fg="green")
        self.toggle_btn.config(text="Stop Monitoring", bg="red")
        self.server_label.config(text="Checking...", fg="blue")
        
        # Start monitoring in separate thread
        self.check_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.check_thread.start()
    
    def stop_monitoring(self):
        self.monitoring = False
        self.status_label.config(text="Monitor: OFF", fg="black")
        self.toggle_btn.config(text="Start Monitoring", bg="green")
        self.server_label.config(text="Server: Unknown", fg="black")

# Run the monitor
if __name__ == "__main__":
    monitor = ServerMonitor()