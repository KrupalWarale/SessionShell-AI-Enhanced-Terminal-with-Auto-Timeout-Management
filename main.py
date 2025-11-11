
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import subprocess
import os
import threading
import time
import psutil

class AutoTerminatorManager:
    def __init__(self, master):
        self.master = master
        master.title("🚀 Auto-Terminator Dashboard")
        master.geometry("900x700")
        master.configure(bg='#2b2b2b')
        
        # Configure style
        self.setup_styles()

        self.ps_process = None
        self.log_file_path = os.path.join(os.environ["TEMP"], "auto_terminator.log")
        self.timestamp_file_path = os.path.join(os.environ["TEMP"], f"auto_terminator_{os.getpid()}.txt")

        self.create_widgets()
        self.update_log_thread = None
        self.stop_update_log = threading.Event()
        self.update_resources_id = None # To store after method ID for cancellation

    def setup_styles(self):
        """Configure modern styling"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure colors
        self.colors = {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'accent': '#4CAF50',
            'danger': '#f44336',
            'warning': '#ff9800',
            'info': '#2196F3',
            'card_bg': '#3c3c3c',
            'border': '#555555'
        }
        
        # Configure ttk styles
        self.style.configure('Title.TLabel', 
                           background=self.colors['bg'], 
                           foreground=self.colors['fg'],
                           font=('Segoe UI', 16, 'bold'))
        
        self.style.configure('Card.TFrame',
                           background=self.colors['card_bg'],
                           relief='flat',
                           borderwidth=1)
        
        self.style.configure('Success.TButton',
                           background=self.colors['accent'],
                           foreground='white',
                           font=('Segoe UI', 10, 'bold'))
        
        self.style.configure('Danger.TButton',
                           background=self.colors['danger'],
                           foreground='white',
                           font=('Segoe UI', 10, 'bold'))

    def create_widgets(self):
        # Main container with padding
        main_frame = tk.Frame(self.master, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="🖥️ Terminal Auto-Terminator", style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame, text="AI-Enhanced Terminal Session Manager", 
                                bg=self.colors['bg'], fg=self.colors['info'], 
                                font=('Segoe UI', 10))
        subtitle_label.pack()
        
        # Control Panel
        control_frame = ttk.Frame(main_frame, style='Card.TFrame', padding=15)
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        control_title = tk.Label(control_frame, text="⚙️ Control Panel", 
                               bg=self.colors['card_bg'], fg=self.colors['fg'],
                               font=('Segoe UI', 12, 'bold'))
        control_title.pack(anchor=tk.W, pady=(0, 10))
        
        # Timeout setting with modern styling
        timeout_frame = tk.Frame(control_frame, bg=self.colors['card_bg'])
        timeout_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.timeout_label = tk.Label(timeout_frame, text="⏱️ Idle Timeout:", 
                                    bg=self.colors['card_bg'], fg=self.colors['fg'],
                                    font=('Segoe UI', 10))
        self.timeout_label.pack(side=tk.LEFT)
        
        self.timeout_entry = tk.Entry(timeout_frame, font=('Segoe UI', 10), width=10,
                                    bg='#4a4a4a', fg='white', insertbackground='white',
                                    relief='flat', bd=5)
        self.timeout_entry.insert(0, "30")
        self.timeout_entry.pack(side=tk.LEFT, padx=(10, 5))
        
        tk.Label(timeout_frame, text="seconds", bg=self.colors['card_bg'], 
                fg=self.colors['fg'], font=('Segoe UI', 10)).pack(side=tk.LEFT)
        
        # Buttons with modern styling
        button_frame = tk.Frame(control_frame, bg=self.colors['card_bg'])
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.start_button = tk.Button(button_frame, text="🚀 Start Terminal", 
                                    command=self.start_terminal,
                                    bg=self.colors['accent'], fg='white',
                                    font=('Segoe UI', 10, 'bold'),
                                    relief='flat', bd=0, padx=20, pady=8,
                                    cursor='hand2')
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_button = tk.Button(button_frame, text="🛑 Stop Terminal", 
                                   command=self.stop_terminal, state=tk.DISABLED,
                                   bg=self.colors['danger'], fg='white',
                                   font=('Segoe UI', 10, 'bold'),
                                   relief='flat', bd=0, padx=20, pady=8,
                                   cursor='hand2')
        self.stop_button.pack(side=tk.LEFT)

        # Status indicator
        self.status_label = tk.Label(button_frame, text="● Stopped", 
                                   bg=self.colors['card_bg'], fg=self.colors['danger'],
                                   font=('Segoe UI', 10, 'bold'))
        self.status_label.pack(side=tk.RIGHT)

        # Resource Dashboard with cards
        dashboard_frame = ttk.Frame(main_frame, style='Card.TFrame', padding=15)
        dashboard_frame.pack(fill=tk.X, pady=(0, 15))
        
        dashboard_title = tk.Label(dashboard_frame, text="📊 System Resources", 
                                 bg=self.colors['card_bg'], fg=self.colors['fg'],
                                 font=('Segoe UI', 12, 'bold'))
        dashboard_title.pack(anchor=tk.W, pady=(0, 15))
        
        # Resource cards in grid
        resources_grid = tk.Frame(dashboard_frame, bg=self.colors['card_bg'])
        resources_grid.pack(fill=tk.X)
        
        # CPU Card
        cpu_card = tk.Frame(resources_grid, bg='#4a4a4a', relief='flat', bd=1)
        cpu_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tk.Label(cpu_card, text="🔥 CPU", bg='#4a4a4a', fg=self.colors['warning'],
                font=('Segoe UI', 9, 'bold')).pack(pady=(8, 2))
        self.cpu_label = tk.Label(cpu_card, text="--%", bg='#4a4a4a', fg='white',
                                font=('Segoe UI', 14, 'bold'))
        self.cpu_label.pack(pady=(0, 8))
        
        # Memory Card
        mem_card = tk.Frame(resources_grid, bg='#4a4a4a', relief='flat', bd=1)
        mem_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(mem_card, text="💾 Memory", bg='#4a4a4a', fg=self.colors['info'],
                font=('Segoe UI', 9, 'bold')).pack(pady=(8, 2))
        self.memory_label = tk.Label(mem_card, text="-- MB", bg='#4a4a4a', fg='white',
                                   font=('Segoe UI', 14, 'bold'))
        self.memory_label.pack(pady=(0, 8))
        
        # Network Card
        net_card = tk.Frame(resources_grid, bg='#4a4a4a', relief='flat', bd=1)
        net_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(net_card, text="🌐 Network", bg='#4a4a4a', fg=self.colors['accent'],
                font=('Segoe UI', 9, 'bold')).pack(pady=(8, 2))
        self.network_label = tk.Label(net_card, text="--", bg='#4a4a4a', fg='white',
                                    font=('Segoe UI', 14, 'bold'))
        self.network_label.pack(pady=(0, 8))
        
        # Power Card
        power_card = tk.Frame(resources_grid, bg='#4a4a4a', relief='flat', bd=1)
        power_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(power_card, text="⚡ Power", bg='#4a4a4a', fg='#9C27B0',
                font=('Segoe UI', 9, 'bold')).pack(pady=(8, 2))
        self.battery_label = tk.Label(power_card, text="--", bg='#4a4a4a', fg='white',
                                    font=('Segoe UI', 14, 'bold'))
        self.battery_label.pack(pady=(0, 8))

        # Log Display with modern styling
        log_frame = ttk.Frame(main_frame, style='Card.TFrame', padding=15)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        log_header = tk.Frame(log_frame, bg=self.colors['card_bg'])
        log_header.pack(fill=tk.X, pady=(0, 10))
        
        log_title = tk.Label(log_header, text="📋 Terminal Logs", 
                           bg=self.colors['card_bg'], fg=self.colors['fg'],
                           font=('Segoe UI', 12, 'bold'))
        log_title.pack(side=tk.LEFT)
        
        clear_btn = tk.Button(log_header, text="🗑️ Clear", command=self.clear_log_display,
                            bg='#666666', fg='white', font=('Segoe UI', 8),
                            relief='flat', bd=0, padx=10, pady=4, cursor='hand2')
        clear_btn.pack(side=tk.RIGHT)

        self.log_text = scrolledtext.ScrolledText(log_frame, width=80, height=15, 
                                                state=tk.DISABLED,
                                                bg='#1e1e1e', fg='#00ff00',
                                                font=('Consolas', 9),
                                                relief='flat', bd=0,
                                                insertbackground='#00ff00')
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def start_terminal(self):
        if self.ps_process and self.ps_process.poll() is None:
            # Process is already running
            return

        # Ensure log file is clean or created
        if os.path.exists(self.log_file_path):
            os.remove(self.log_file_path)

        # Get timeout value from entry
        try:
            timeout_value = int(self.timeout_entry.get())
            if timeout_value <= 0:
                raise ValueError("Timeout must be a positive integer.")
        except ValueError as e:
            messagebox.showerror("Invalid Timeout", str(e))
            return

        # Use subprocess.Popen to launch the PowerShell script in a new window
        try:
            script_path = os.path.join(os.getcwd(), "auto-terminator.ps1")
            self.ps_process = subprocess.Popen(
                [
                    "powershell.exe",
                    "-ExecutionPolicy", "Bypass",
                    "-NoExit",
                    "-File", script_path,
                    "-Timeout", str(timeout_value)
                ],
                creationflags=subprocess.CREATE_NEW_CONSOLE  # Opens in a new console window
            )
            # Get the psutil process object
            try:
                self.psutil_process = psutil.Process(self.ps_process.pid)
            except psutil.NoSuchProcess:
                self.psutil_process = None
                print("Could not get psutil process object. Resource monitoring will be limited.")

            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_label.config(text="● Running", fg=self.colors['accent'])
            self.start_log_updater()
            self.update_resource_dashboard()
            print(f"Launched auto-terminator.ps1 with PID: {self.ps_process.pid} and Timeout: {timeout_value}s")
        except Exception as e:
            print(f"Error launching PowerShell: {e}")
            self.stop_button.config(state=tk.DISABLED)
            self.start_button.config(state=tk.NORMAL)

    def stop_terminal(self):
        if self.ps_process and self.ps_process.poll() is None:
            print(f"Terminating auto-terminator process (PID: {self.ps_process.pid})...")
            self.stop_log_updater()
            self.cancel_resource_updates()
            try:
                # Use taskkill for graceful termination on Windows
                subprocess.run(["taskkill", "/PID", str(self.ps_process.pid), "/T", "/F"], check=True)
                print("Process terminated.")
            except subprocess.CalledProcessError as e:
                print(f"Error terminating process: {e}")
            self.ps_process = None
            self.psutil_process = None

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="● Stopped", fg=self.colors['danger'])
        self.clear_log_display()
        self.reset_resource_dashboard()

    def start_log_updater(self):
        self.stop_update_log.clear()
        self.update_log_thread = threading.Thread(target=self._update_log_display)
        self.update_log_thread.daemon = True  # Allows the thread to exit with the main program
        self.update_log_thread.start()

    def stop_log_updater(self):
        self.stop_update_log.set()
        if self.update_log_thread and self.update_log_thread.is_alive():
            self.update_log_thread.join(timeout=1) # Wait for thread to finish

    def _update_log_display(self):
        last_read_position = 0
        while not self.stop_update_log.is_set():
            try:
                if os.path.exists(self.log_file_path):
                    with open(self.log_file_path, "r", encoding="utf-8") as f:
                        f.seek(last_read_position)
                        new_content = f.read()
                        if new_content:
                            self.log_text.config(state=tk.NORMAL)
                            self.log_text.insert(tk.END, new_content)
                            self.log_text.see(tk.END) # Scroll to the end
                            self.log_text.config(state=tk.DISABLED)
                            last_read_position = f.tell()
            except FileNotFoundError:
                pass # Log file might not be created yet
            except Exception as e:
                print(f"Error reading log file: {e}")
            
            time.sleep(0.5) # Check every 500ms

    def update_resource_dashboard(self):
        cpu_percent = "--"
        memory_mb = "--"
        network_connections = "--"
        battery_status = "--"

        if self.psutil_process and self.psutil_process.is_running():
            try:
                cpu_percent = self.psutil_process.cpu_percent(interval=0.1) # Non-blocking
                mem_info = self.psutil_process.memory_info()
                memory_mb = f"{(mem_info.rss / (1024 * 1024)):.2f}"

                # Get all child processes
                children = self.psutil_process.children(recursive=True)
                all_procs = [self.psutil_process] + children
                total_connections = 0
                for proc in all_procs:
                    try:
                        total_connections += len(proc.connections(kind="inet"))
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                network_connections = str(total_connections)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                self.psutil_process = None # Process might have just ended or access denied

        # Terminal Power Consumption
        power_consumption = "--"
        if self.psutil_process and self.psutil_process.is_running():
            try:
                # Get CPU usage and estimate power consumption
                cpu_usage = self.psutil_process.cpu_percent(interval=0.1)
                memory_usage = self.psutil_process.memory_info().rss / (1024 * 1024)  # MB
                
                # Estimate power consumption based on CPU and memory usage
                # Rough estimation: Base consumption + CPU factor + Memory factor
                base_power = 0.5  # Base power consumption in watts
                cpu_power = (cpu_usage / 100) * 2.0  # CPU can consume up to 2W
                memory_power = (memory_usage / 1000) * 0.1  # Memory factor
                
                total_power = base_power + cpu_power + memory_power
                power_consumption = f"{total_power:.2f}W"
                
                # Get all child processes for total consumption
                children = self.psutil_process.children(recursive=True)
                if children:
                    child_power = 0
                    for child in children:
                        try:
                            child_cpu = child.cpu_percent(interval=0.1)
                            child_power += (child_cpu / 100) * 0.5  # Child processes consume less
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                    total_power += child_power
                    power_consumption = f"{total_power:.2f}W"
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                power_consumption = "N/A"
        
        battery_status = power_consumption

        self.cpu_label.config(text=f"{cpu_percent}%")
        self.memory_label.config(text=f"{memory_mb} MB")
        self.network_label.config(text=f"{network_connections}")
        self.battery_label.config(text=f"{battery_status}")

        self.update_resources_id = self.master.after(1000, self.update_resource_dashboard) # Update every 1 second

    def cancel_resource_updates(self):
        if self.update_resources_id:
            self.master.after_cancel(self.update_resources_id)
            self.update_resources_id = None

    def reset_resource_dashboard(self):
        self.cpu_label.config(text="--%")
        self.memory_label.config(text="-- MB")
        self.network_label.config(text="--")
        self.battery_label.config(text="--")

    def clear_log_display(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def on_closing(self):
        self.stop_terminal()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoTerminatorManager(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop() 