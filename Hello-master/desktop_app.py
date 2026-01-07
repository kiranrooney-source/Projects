import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
import threading
import getpass
import os

class ServerQueryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Server Query Automation")
        self.root.geometry("700x650")
        
        self.connected = False
        self.server_url = ""
        self.auth_token = None
        self.databases = []
        
        self.create_widgets()
    
    def create_widgets(self):
        # Server Connection Frame
        conn_frame = ttk.LabelFrame(self.root, text="Server Connection", padding="10")
        conn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(conn_frame, text="Server Name:").grid(row=0, column=0, sticky="w")
        self.server_name_entry = ttk.Entry(conn_frame, width=30)
        self.server_name_entry.grid(row=0, column=1, padx=5)
        self.server_name_entry.insert(0, "localhost")
        
        # Windows Authentication checkbox
        self.use_windows_auth = tk.BooleanVar(value=True)
        self.windows_auth_cb = ttk.Checkbutton(conn_frame, text="Use Windows Authentication", 
                                             variable=self.use_windows_auth, command=self.toggle_auth_fields)
        self.windows_auth_cb.grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        
        ttk.Label(conn_frame, text="Username:").grid(row=2, column=0, sticky="w")
        self.username_entry = ttk.Entry(conn_frame, width=30, state="disabled")
        self.username_entry.grid(row=2, column=1, padx=5)
        self.username_entry.insert(0, getpass.getuser())
        
        ttk.Label(conn_frame, text="Password:").grid(row=3, column=0, sticky="w")
        self.password_entry = ttk.Entry(conn_frame, width=30, show="*", state="disabled")
        self.password_entry.grid(row=3, column=1, padx=5)
        self.password_entry.insert(0, "[Windows Auth]")
        
        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self.connect_server)
        self.connect_btn.grid(row=0, column=2, rowspan=4, padx=5, sticky="ns")
        
        self.status_label = ttk.Label(conn_frame, text="Status: Disconnected", foreground="red")
        self.status_label.grid(row=4, column=0, columnspan=3, sticky="w", pady=5)
        
        # Bind server name entry to auto-connect
        self.server_name_entry.bind('<Return>', self.on_server_name_enter)
        self.server_name_entry.bind('<FocusOut>', self.on_server_name_change)
        
        # Database Selection Frame
        db_frame = ttk.LabelFrame(self.root, text="Database Selection", padding="10")
        db_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(db_frame, text="Available Databases:").grid(row=0, column=0, sticky="w")
        self.db_combo = ttk.Combobox(db_frame, width=40, state="readonly")
        self.db_combo.grid(row=0, column=1, padx=5)
        
        self.refresh_db_btn = ttk.Button(db_frame, text="Refresh", command=self.refresh_databases, state="disabled")
        self.refresh_db_btn.grid(row=0, column=2, padx=5)
        
        # Query Input Frame
        query_frame = ttk.LabelFrame(self.root, text="Query Requirements", padding="10")
        query_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ttk.Label(query_frame, text="Enter your requirements:").pack(anchor="w")
        self.query_text = scrolledtext.ScrolledText(query_frame, height=8, width=70)
        self.query_text.pack(fill="both", expand=True, pady=5)
        
        # Buttons Frame
        btn_frame = ttk.Frame(query_frame)
        btn_frame.pack(fill="x", pady=5)
        
        self.execute_btn = ttk.Button(btn_frame, text="Execute Query", command=self.execute_query, state="disabled")
        self.execute_btn.pack(side="left", padx=5)
        
        self.clear_btn = ttk.Button(btn_frame, text="Clear", command=self.clear_query)
        self.clear_btn.pack(side="left", padx=5)
        
        # Results Frame
        results_frame = ttk.LabelFrame(self.root, text="Results", padding="10")
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=8, width=70)
        self.results_text.pack(fill="both", expand=True)
    
    def toggle_auth_fields(self):
        if self.use_windows_auth.get():
            self.username_entry.config(state="disabled")
            self.password_entry.config(state="disabled")
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, getpass.getuser())
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, "[Windows Auth]")
        else:
            self.username_entry.config(state="normal")
            self.password_entry.config(state="normal")
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
    
    def on_server_name_enter(self, event):
        self.auto_connect_to_server()
    
    def on_server_name_change(self, event):
        server_name = self.server_name_entry.get().strip()
        if server_name and not self.connected:
            self.auto_connect_to_server()
    
    def auto_connect_to_server(self):
        server_name = self.server_name_entry.get().strip()
        if server_name and self.use_windows_auth.get():
            self.connect_server()
    
    def connect_server(self):
        if self.connected:
            self.disconnect_server()
            return
            
        server_name = self.server_name_entry.get().strip()
        
        if not server_name:
            messagebox.showerror("Error", "Please enter server name")
            return
        
        # Generate server URL from server name
        self.server_url = f"http://{server_name}:8000"
        
        # Get credentials based on authentication method
        if self.use_windows_auth.get():
            username = getpass.getuser()
            password = "windows_auth_token"  # Placeholder for Windows auth
        else:
            username = self.username_entry.get().strip()
            password = self.password_entry.get().strip()
            if not username or not password:
                messagebox.showerror("Error", "Please enter username and password")
                return
        
        self.status_label.config(text="Status: Connecting...", foreground="orange")
        self.connect_btn.config(state="disabled")
        
        def test_connection():
            try:
                # First check server health
                health_response = requests.get(f"{self.server_url}/health", timeout=5)
                if health_response.status_code != 200:
                    self.root.after(0, self.update_connection_status, False, "Server health check failed")
                    return
                
                # Authenticate with server
                auth_data = {
                    "username": username, 
                    "password": password,
                    "auth_type": "windows" if self.use_windows_auth.get() else "standard"
                }
                response = requests.post(f"{self.server_url}/auth", json=auth_data, timeout=5)
                
                if response.status_code == 200:
                    result = response.json()
                    self.auth_token = result.get("token")
                    self.connected = True
                    self.root.after(0, self.update_connection_status, True, None, server_name)
                    self.root.after(0, self.load_databases)
                else:
                    error_msg = "Authentication failed"
                    if response.status_code == 401:
                        error_msg = "Invalid credentials or Windows authentication not supported"
                    self.root.after(0, self.update_connection_status, False, error_msg)
            except requests.exceptions.ConnectionError:
                self.root.after(0, self.update_connection_status, False, f"Cannot connect to {server_name}:8000. Check server name and ensure server is running.")
            except requests.exceptions.Timeout:
                self.root.after(0, self.update_connection_status, False, "Connection timeout. Server may be slow or unreachable.")
            except requests.exceptions.RequestException as e:
                self.root.after(0, self.update_connection_status, False, f"Connection error: {str(e)}")
        
        threading.Thread(target=test_connection, daemon=True).start()
    
    def disconnect_server(self):
        self.connected = False
        self.auth_token = None
        self.databases = []
        self.db_combo['values'] = []
        self.db_combo.set('')
        self.status_label.config(text="Status: Disconnected", foreground="red")
        self.connect_btn.config(text="Connect", state="normal")
        self.execute_btn.config(state="disabled")
        self.refresh_db_btn.config(state="disabled")
    
    def update_connection_status(self, connected, error_msg=None, server_name=None):
        self.connect_btn.config(state="normal")
        
        if connected:
            status_text = f"Status: Connected to {server_name}" if server_name else "Status: Connected & Authenticated"
            self.status_label.config(text=status_text, foreground="green")
            self.execute_btn.config(state="normal")
            self.refresh_db_btn.config(state="normal")
            self.connect_btn.config(text="Disconnect")
            messagebox.showinfo("Success", f"Successfully connected to {server_name}!")
        else:
            self.status_label.config(text="Status: Connection Failed", foreground="red")
            self.execute_btn.config(state="disabled")
            self.refresh_db_btn.config(state="disabled")
            self.connect_btn.config(text="Connect")
            error_text = error_msg or "Failed to connect to server"
            messagebox.showerror("Connection Error", error_text)
    
    def load_databases(self):
        def fetch_databases():
            try:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                response = requests.get(f"{self.server_url}/databases", headers=headers, timeout=10)
                
                if response.status_code == 200:
                    databases = response.json().get("databases", [])
                    self.root.after(0, self.update_database_list, databases)
                else:
                    self.root.after(0, self.show_db_error, "Failed to fetch databases")
            except requests.exceptions.RequestException as e:
                self.root.after(0, self.show_db_error, str(e))
        
        threading.Thread(target=fetch_databases, daemon=True).start()
    
    def update_database_list(self, databases):
        self.databases = databases
        self.db_combo['values'] = databases
        if databases:
            self.db_combo.current(0)
    
    def show_db_error(self, error_msg):
        messagebox.showerror("Database Error", f"Error loading databases: {error_msg}")
    
    def refresh_databases(self):
        if self.connected:
            self.load_databases()
    
    def execute_query(self):
        requirements = self.query_text.get("1.0", tk.END).strip()
        selected_db = self.db_combo.get()
        
        if not requirements:
            messagebox.showwarning("Warning", "Please enter your requirements")
            return
        if not selected_db:
            messagebox.showwarning("Warning", "Please select a database")
            return
        
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, "Processing query...\n")
        
        def send_query():
            try:
                payload = {
                    "requirements": requirements,
                    "database": selected_db
                }
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                response = requests.post(f"{self.server_url}/query", 
                                       json=payload, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    self.root.after(0, self.display_results, result)
                else:
                    error_msg = f"Server error: {response.status_code}"
                    self.root.after(0, self.display_error, error_msg)
            except requests.exceptions.RequestException as e:
                self.root.after(0, self.display_error, f"Request failed: {str(e)}")
        
        threading.Thread(target=send_query, daemon=True).start()
    
    def display_results(self, result):
        self.results_text.delete("1.0", tk.END)
        if isinstance(result, dict):
            formatted_result = json.dumps(result, indent=2)
        else:
            formatted_result = str(result)
        self.results_text.insert(tk.END, formatted_result)
    
    def display_error(self, error_msg):
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, f"Error: {error_msg}")
    
    def clear_query(self):
        self.query_text.delete("1.0", tk.END)
        self.results_text.delete("1.0", tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerQueryApp(root)
    root.mainloop()