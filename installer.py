import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from threading import Thread
import platform
import requests
import tempfile
import shutil
import time
import psutil

# Software Information
__version__ = "1.0.1"
__author__ = "Devharris"
__credits__ = [
    "Developer: Harris Sagiris",
]
__about__ = """
Zapinstall Installation Tool

This tool provides an easy-to-use graphical interface for installing common 
software packages across different operating systems. It supports Windows, 
Linux, and macOS platforms using their native package managers (winget, 
apt/snap, and homebrew respectively).

Features:
- Categorized software selection
- Cross-platform compatibility 
- Progress tracking
- Parallel installation
- Error handling
- System resource monitoring

Copyright © 2025. All rights reserved.
"""

def check_windows_activation():
    try:
        result = subprocess.run(['cscript', '//nologo', '%windir%\\system32\\slmgr.vbs', '/xpr'], 
                              capture_output=True, text=True, shell=True)
        return "permanently activated" in result.stdout.lower()
    except:
        return False

def download_activator():
    url = "https://raw.githubusercontent.com/massgravel/Microsoft-Activation-Scripts/master/MAS/All-In-One-Version/MAS_AIO.cmd"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open("windows_activator.cmd", "wb") as f:
                f.write(response.content)
            return True
    except:
        return False
    return False

def check_system_resources():
    """Check system resources before installation"""
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    warnings = []
    if cpu_percent > 80:
        warnings.append("High CPU usage detected")
    if memory.percent > 80:
        warnings.append("Low memory available") 
    if disk.percent > 90:
        warnings.append("Low disk space")
        
    return warnings

class InstallationWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Zapinstall")
        self.geometry("350x250")
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "zapinstall.png")
        if os.path.exists(icon_path):
            icon = tk.PhotoImage(file=icon_path)
            self.iconphoto(True, icon)
        
        # Simple black and white theme
        style = ttk.Style()
        style.configure("Custom.TFrame", background="white")
        style.configure("Custom.TLabel", foreground="black", background="white")
        style.configure("Custom.Horizontal.TProgressbar", background="black")
        
        self.configure(bg="white")
        
        # Main container
        main_frame = ttk.Frame(self, style="Custom.TFrame")
        main_frame.pack(fill='both', expand=True, padx=3, pady=3)
        
        # Header
        header = ttk.Label(main_frame, text="Installing Software", font=('Arial', 11, 'bold'), style="Custom.TLabel")
        header.pack(pady=(0,3))
        
        # Progress contents
        self.output_text = scrolledtext.ScrolledText(main_frame, height=10, font=('Consolas', 9), bg="white", fg="black")
        self.output_text.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Progress bar frame
        progress_frame = ttk.Frame(main_frame, style="Custom.TFrame")
        progress_frame.pack(fill='x', pady=3)
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate', style="Custom.Horizontal.TProgressbar")
        self.progress.pack(fill='x')
        
        self.status_label = ttk.Label(progress_frame, text="Ready to install", font=('Arial', 9), style="Custom.TLabel")
        self.status_label.pack(pady=(2,0))

class AboutWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("About")
        self.geometry("350x250")
        self.configure(bg="white")
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "zapinstall.png")
        if os.path.exists(icon_path):
            icon = tk.PhotoImage(file=icon_path)
            self.iconphoto(True, icon)
        
        style = ttk.Style()
        style.configure("About.TLabel", foreground="black", background="white")
        
        ttk.Label(self, text=f"Software Installer v{__version__}", font=('Arial', 11, 'bold'), style="About.TLabel").pack(pady=8)
        ttk.Label(self, text=f"By {__author__}", style="About.TLabel").pack()
        
        credits_frame = ttk.LabelFrame(self, text="Credits", style="About.TLabel")
        credits_frame.pack(fill='x', padx=8, pady=3)
        for credit in __credits__:
            ttk.Label(credits_frame, text=credit, style="About.TLabel").pack(anchor='w')
            
        about_frame = ttk.LabelFrame(self, text="About", style="About.TLabel")
        about_frame.pack(fill='both', expand=True, padx=8, pady=3)
        about_text = scrolledtext.ScrolledText(about_frame, wrap=tk.WORD, height=6, bg="white", fg="black")
        about_text.pack(fill='both', expand=True, padx=3, pady=3)
        about_text.insert('1.0', __about__)
        about_text.configure(state='disabled')

class SoftwareInstaller:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title(f"Zapinstall v{__version__}")
        self.window.geometry("500x600")
        self.window.configure(bg="white")
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "zapinstall.png")
        if os.path.exists(icon_path):
            icon = tk.PhotoImage(file=icon_path)
            self.window.iconphoto(True, icon)
        
        # Configure style
        style = ttk.Style()
        style.configure("Category.TLabelframe", font=('Arial', 9, 'bold'), background="white", foreground="black")
        style.configure("Category.TLabelframe.Label", font=('Arial', 9, 'bold'), background="white", foreground="black")
        style.configure("Custom.TButton", padding=3, background="white", foreground="black")
        style.configure("Custom.TCheckbutton", background="white", foreground="black")
        style.configure("Disabled.TButton", padding=3, background="gray", foreground="gray")
        
        # Check Windows activation status
        self.is_activated = check_windows_activation() if platform.system() == "Windows" else False
        
        # Extended software dictionary
        self.software = {
            'Development': {
                'VS Code': {'cmd': 'winget install Microsoft.VisualStudioCode', 'linux': 'sudo snap install code --classic', 'mac': 'brew install --cask visual-studio-code'},
                'PyCharm': {'cmd': 'winget install JetBrains.PyCharm.Community', 'linux': 'sudo snap install pycharm-community --classic', 'mac': 'brew install --cask pycharm-ce'},
                'Git': {'cmd': 'winget install Git.Git', 'linux': 'sudo apt install git -y', 'mac': 'brew install git'},
                'Python': {'cmd': 'winget install Python.Python.3', 'linux': 'sudo apt install python3 -y', 'mac': 'brew install python3'},
                'Node.js': {'cmd': 'winget install OpenJS.NodeJS', 'linux': 'sudo apt install nodejs -y', 'mac': 'brew install node'},
                'Docker': {'cmd': 'winget install Docker.DockerDesktop', 'linux': 'sudo apt install docker.io -y', 'mac': 'brew install --cask docker'},
                'IntelliJ': {'cmd': 'winget install JetBrains.IntelliJIDEA.Community', 'linux': 'sudo snap install intellij-idea-community --classic', 'mac': 'brew install --cask intellij-idea-ce'},
                'Android Studio': {'cmd': 'winget install Google.AndroidStudio', 'linux': 'sudo snap install android-studio --classic', 'mac': 'brew install --cask android-studio'},
                'Sublime Text': {'cmd': 'winget install SublimeHQ.SublimeText', 'linux': 'sudo snap install sublime-text --classic', 'mac': 'brew install --cask sublime-text'},
                'Eclipse': {'cmd': 'winget install EclipseFoundation.Eclipse', 'linux': 'sudo snap install eclipse --classic', 'mac': 'brew install --cask eclipse-ide'}
            },
            'Browsers': {
                'Chrome': {'cmd': 'winget install Google.Chrome', 'linux': 'wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && sudo dpkg -i google-chrome-stable_current_amd64.deb', 'mac': 'brew install --cask google-chrome'},
                'Firefox': {'cmd': 'winget install Mozilla.Firefox', 'linux': 'sudo apt install firefox -y', 'mac': 'brew install --cask firefox'},
                'Brave': {'cmd': 'winget install BraveSoftware.BraveBrowser', 'linux': 'sudo snap install brave', 'mac': 'brew install --cask brave-browser'},
                'Opera': {'cmd': 'winget install Opera.Opera', 'linux': 'sudo snap install opera', 'mac': 'brew install --cask opera'},
                'Edge': {'cmd': 'winget install Microsoft.Edge', 'linux': 'sudo snap install microsoft-edge-stable --classic', 'mac': 'brew install --cask microsoft-edge'},
                'Vivaldi': {'cmd': 'winget install VivaldiTechnologies.Vivaldi', 'linux': 'sudo snap install vivaldi', 'mac': 'brew install --cask vivaldi'},
                'Tor Browser': {'cmd': 'winget install TorProject.TorBrowser', 'linux': 'sudo apt install torbrowser-launcher -y', 'mac': 'brew install --cask tor-browser'}
            },
            'Utilities': {
                'Postman': {'cmd': 'winget install Postman.Postman', 'linux': 'sudo snap install postman', 'mac': 'brew install --cask postman'},
                '7-Zip': {'cmd': 'winget install 7zip.7zip', 'linux': 'sudo apt install p7zip-full -y', 'mac': 'brew install p7zip'},
                'VLC': {'cmd': 'winget install VideoLAN.VLC', 'linux': 'sudo apt install vlc -y', 'mac': 'brew install --cask vlc'},
                'OBS Studio': {'cmd': 'winget install OBSProject.OBSStudio', 'linux': 'sudo apt install obs-studio -y', 'mac': 'brew install --cask obs'},
                'FileZilla': {'cmd': 'winget install TimKosse.FileZilla', 'linux': 'sudo apt install filezilla -y', 'mac': 'brew install --cask filezilla'},
                'WinSCP': {'cmd': 'winget install WinSCP.WinSCP', 'linux': 'sudo apt install winscp -y', 'mac': 'brew install --cask winscp'},
                'Putty': {'cmd': 'winget install PuTTY.PuTTY', 'linux': 'sudo apt install putty -y', 'mac': 'brew install --cask putty'},
                'TeamViewer': {'cmd': 'winget install TeamViewer.TeamViewer', 'linux': 'sudo snap install teamviewer', 'mac': 'brew install --cask teamviewer'},
                'Remmina': {'cmd': 'winget install Remmina.Remmina', 'linux': 'sudo apt install remmina -y', 'mac': 'brew install --cask remmina'},
                'Etcher': {'cmd': 'winget install Balena.Etcher', 'linux': 'sudo apt install balena-etcher -y', 'mac': 'brew install --cask balenaetcher'}
            },
            'Communication': {
                'Discord': {'cmd': 'winget install Discord.Discord', 'linux': 'sudo snap install discord', 'mac': 'brew install --cask discord'},
                'Slack': {'cmd': 'winget install SlackTechnologies.Slack', 'linux': 'sudo snap install slack', 'mac': 'brew install --cask slack'},
                'Zoom': {'cmd': 'winget install Zoom.Zoom', 'linux': 'sudo snap install zoom-client', 'mac': 'brew install --cask zoom'},
                'Teams': {'cmd': 'winget install Microsoft.Teams', 'linux': 'sudo snap install teams', 'mac': 'brew install --cask microsoft-teams'},
                'Skype': {'cmd': 'winget install Microsoft.Skype', 'linux': 'sudo snap install skype', 'mac': 'brew install --cask skype'},
                'Telegram': {'cmd': 'winget install Telegram.TelegramDesktop', 'linux': 'sudo snap install telegram-desktop', 'mac': 'brew install --cask telegram'},
                'Signal': {'cmd': 'winget install OpenWhisperSystems.Signal', 'linux': 'sudo snap install signal-desktop', 'mac': 'brew install --cask signal'},
                'Element': {'cmd': 'winget install Element.Element', 'linux': 'sudo apt install element-desktop -y', 'mac': 'brew install --cask element'}
            },
            'Media': {
                'Spotify': {'cmd': 'winget install Spotify.Spotify', 'linux': 'sudo snap install spotify', 'mac': 'brew install --cask spotify'},
                'Steam': {'cmd': 'winget install Valve.Steam', 'linux': 'sudo apt install steam -y', 'mac': 'brew install --cask steam'},
                'Audacity': {'cmd': 'winget install Audacity.Audacity', 'linux': 'sudo apt install audacity -y', 'mac': 'brew install --cask audacity'},
                'GIMP': {'cmd': 'winget install GIMP.GIMP', 'linux': 'sudo apt install gimp -y', 'mac': 'brew install --cask gimp'},
                'Blender': {'cmd': 'winget install BlenderFoundation.Blender', 'linux': 'sudo snap install blender --classic', 'mac': 'brew install --cask blender'},
                'Inkscape': {'cmd': 'winget install Inkscape.Inkscape', 'linux': 'sudo apt install inkscape -y', 'mac': 'brew install --cask inkscape'},
                'Krita': {'cmd': 'winget install KDE.Krita', 'linux': 'sudo snap install krita', 'mac': 'brew install --cask krita'},
                'HandBrake': {'cmd': 'winget install HandBrake.HandBrake', 'linux': 'sudo snap install handbrake-jz', 'mac': 'brew install --cask handbrake'},
                'OBS Studio': {'cmd': 'winget install OBSProject.OBSStudio', 'linux': 'sudo apt install obs-studio -y', 'mac': 'brew install --cask obs'},
                'DaVinci Resolve': {'cmd': 'winget install Blackmagic.DaVinciResolve', 'linux': 'sudo snap install davinci-resolve', 'mac': 'brew install --cask davinci-resolve'}
            },
            'Security': {
                'Wireshark': {'cmd': 'winget install WiresharkFoundation.Wireshark', 'linux': 'sudo apt install wireshark -y', 'mac': 'brew install --cask wireshark'},
                'Bitwarden': {'cmd': 'winget install Bitwarden.Bitwarden', 'linux': 'sudo snap install bitwarden', 'mac': 'brew install --cask bitwarden'},
                'KeePass': {'cmd': 'winget install DominikReichl.KeePass', 'linux': 'sudo apt install keepass2 -y', 'mac': 'brew install --cask keepass'},
                'VeraCrypt': {'cmd': 'winget install IDRIX.VeraCrypt', 'linux': 'sudo apt install veracrypt -y', 'mac': 'brew install --cask veracrypt'},
                'Nmap': {'cmd': 'winget install Insecure.Nmap', 'linux': 'sudo apt install nmap -y', 'mac': 'brew install nmap'},
                'OpenVPN': {'cmd': 'winget install OpenVPNTechnologies.OpenVPN', 'linux': 'sudo apt install openvpn -y', 'mac': 'brew install --cask openvpn-connect'}
            }
        }

        self.selected_software = {}
        self.setup_gui()

    def activate_windows(self):
        if not os.path.exists("windows_activator.cmd"):
            if not download_activator():
                messagebox.showerror("Error", "Failed to download Windows activator")
                return
                
        try:
            # Run as administrator
            subprocess.run(["runas", "/user:Administrator", "windows_activator.cmd"], shell=True)
            time.sleep(5)  # Wait for activation to complete
            
            self.is_activated = check_windows_activation()
            if self.is_activated:
                self.activation_label.config(text="Windows is activated!")
                self.activate_btn.configure(state="disabled")
                messagebox.showinfo("Success", "Windows has been activated successfully!")
            else:
                messagebox.showerror("Error", "Activation failed. Please try again.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run activator: {str(e)}")
        
        # Clean up
        try:
            if os.path.exists("windows_activator.cmd"):
                os.remove("windows_activator.cmd")
        except:
            pass

    def setup_gui(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.window, padding=3)
        main_frame.pack(expand=1, fill='both')
        
        # Header with About button and Windows Activation
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0,3))
        
        ttk.Label(header_frame, text="Select Software to Install", font=('Arial', 11, 'bold'), foreground="black", background="white").pack(side='left')
        ttk.Button(header_frame, text="About", command=self.show_about, style="Custom.TButton").pack(side='right')

        # Windows Activation Section (if on Windows)
        if platform.system() == "Windows":
            activation_frame = ttk.Frame(main_frame)
            activation_frame.pack(fill='x', pady=3)
            
            self.activate_btn = ttk.Button(activation_frame, text="Activate Windows", 
                                         command=self.activate_windows,
                                         state="disabled" if self.is_activated else "normal")
            self.activate_btn.pack(side='left')
            
            self.activation_label = ttk.Label(activation_frame, 
                                            text="Windows is activated!" if self.is_activated else "",
                                            foreground="black", background="white")
            self.activation_label.pack(side='left', padx=5)

        # Create outer frame for scrolling
        outer_frame = ttk.Frame(main_frame)
        outer_frame.pack(fill='both', expand=True)

        # Add canvas and scrollbar
        canvas = tk.Canvas(outer_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)

        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        # Create category frames in 2 columns
        col, row = 0, 0
        for category, software_dict in self.software.items():
            category_frame = ttk.LabelFrame(inner_frame, text=category, padding=3, style="Category.TLabelframe")
            category_frame.grid(row=row, column=col, sticky='nsew', padx=2, pady=2)
            
            for i, (name, _) in enumerate(software_dict.items()):
                var = tk.BooleanVar()
                self.selected_software[name] = var
                cb = ttk.Checkbutton(category_frame, text=name, variable=var, style="Custom.TCheckbutton")
                cb.grid(row=i, column=0, sticky='w', padx=3, pady=1)
            
            col = (col + 1) % 2
            if col == 0:
                row += 1

        inner_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=3)
        
        ttk.Button(btn_frame, text="Select All", command=self.select_all, style="Custom.TButton").pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Deselect All", command=self.deselect_all, style="Custom.TButton").pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Install Selected", command=self.install_selected, style="Custom.TButton").pack(side='right', padx=2)

    def show_about(self):
        AboutWindow(self.window)

    def select_all(self):
        for var in self.selected_software.values():
            var.set(True)

    def deselect_all(self):
        for var in self.selected_software.values():
            var.set(False)

    def log_output(self, message):
        self.install_window.output_text.insert(tk.END, f"{message}\n")
        self.install_window.output_text.see(tk.END)
        self.install_window.output_text.update()

    def install_selected(self):
        selected = [sw for sw, var in self.selected_software.items() if var.get()]
        
        if not selected:
            messagebox.showwarning("Warning", "Please select software to install")
            return

        # Check system resources before installation
        warnings = check_system_resources()
        if warnings:
            warning_msg = "\n".join(warnings)
            if not messagebox.askyesno("System Resource Warning", 
                                     f"The following issues were detected:\n\n{warning_msg}\n\nDo you want to continue anyway?"):
                return

        # Check package manager availability
        os_type = 'cmd' if sys.platform == 'win32' else 'linux' if sys.platform.startswith('linux') else 'mac'
        
        if os_type == 'cmd':
            try:
                subprocess.run(['winget', '--version'], capture_output=True, check=True)
            except:
                messagebox.showerror("Error", "Winget package manager not found. Please install it first.")
                return
        elif os_type == 'mac':
            try:
                subprocess.run(['brew', '--version'], capture_output=True, check=True) 
            except:
                messagebox.showerror("Error", "Homebrew package manager not found. Please install it first.")
                return
        elif os_type == 'linux':
            try:
                subprocess.run(['apt', '--version'], capture_output=True, check=True)
            except:
                messagebox.showerror("Error", "APT package manager not found.")
                return
            try:
                subprocess.run(['snap', '--version'], capture_output=True, check=True)
            except:
                self.log_output("Warning: Snap not found. Some packages may fail to install.")

        self.install_window = InstallationWindow(self.window)
        self.install_window.output_text.delete(1.0, tk.END)
        self.install_window.progress['value'] = 0
        Thread(target=self.install_thread, args=(selected,), daemon=True).start()

    def install_thread(self, selected):
        total = len(selected)
        os_type = 'cmd' if sys.platform == 'win32' else 'linux' if sys.platform.startswith('linux') else 'mac'
        
        self.log_output(f"Installing {total} packages...")
        
        if os_type == 'linux':
            try:
                self.log_output("Updating package lists...")
                subprocess.run('sudo apt update', shell=True, check=True)
            except:
                self.log_output("Warning: Failed to update package lists")
        
        for i, software in enumerate(selected, 1):
            try:
                self.install_window.status_label.config(text=f"Installing {software}...")
                self.log_output(f"\nInstalling {software}...")
                
                cmd = None
                for category in self.software.values():
                    if software in category:
                        cmd = category[software][os_type]
                        break
                
                if cmd:
                    process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if process.returncode == 0:
                        self.log_output(f"✓ {software} installed successfully")
                    else:
                        raise Exception(process.stderr)
                
                progress = (i / total) * 100
                self.install_window.progress['value'] = progress
                
            except Exception as e:
                self.log_output(f"❌ Failed to install {software}: {str(e)}")
                messagebox.showerror("Error", f"Failed to install {software}")

        self.install_window.status_label.config(text="Installation complete!")
        self.log_output("\nAll installations completed!")
        messagebox.showinfo("Success", "Installation complete!")

    def run(self):
        self.window.mainloop()

def main():
    installer = SoftwareInstaller()
    installer.run()

if __name__ == "__main__":
    main()
