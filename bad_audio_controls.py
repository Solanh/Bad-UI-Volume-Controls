import tkinter as tk
import os
import platform
import ctypes

try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
except ImportError:
    print("Warning: pycaw module not found. Install it with `pip install pycaw comtypes` on Windows.")
    
    # === DPI Awareness for Windows ===
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except AttributeError:
    pass  # Ignore errors on non-Windows systems

class BadAudioControls:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Bad Audio Controls")
        self.center_window(root, width=500, height=500)  # Center window
        self.root.resizable(False, False)
        
        self.current_vol = self.get_system_volume()  # Get system volume on startup
        
        self.create_widgets()  # Create UI elements
    
    def create_widgets(self):
        # Main Frame
        main_frame = tk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Allow rows and columns to expand
        main_frame.grid_rowconfigure(0, weight=1)  
        main_frame.grid_rowconfigure(1, weight=1)  
        main_frame.grid_columnconfigure(0, weight=1)  
        main_frame.grid_columnconfigure(1, weight=1)

        # Title Label
        self.label = tk.Label(main_frame, text="Bad Audio Controls", font=("Arial", 14, "bold"))
        self.label.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=5)

        # Volume Up Button
        self.button = tk.Button(main_frame, text="Volume Up!", command=self.vol_up)    
        self.button.grid(row=1, column=0, pady=5, padx=16, sticky="ew") 

        # Volume Label
        self.volume_label = tk.Label(main_frame, text=f"Volume: {self.current_vol}%")
        self.volume_label.grid(row=1, column=1, pady=5, padx=16, sticky="nsew")

        # Read-Only Volume Slider (Status Bar)
        self.volume_slider = tk.Scale(
            main_frame, 
            length=300, 
            sliderlength=15, 
            width=30, 
            orient="vertical", 
            from_=100, 
            to=0,  # Flipped for intuitive display
            label="Volume"
        )
        self.volume_slider.set(self.current_vol)  # Set initial volume
        self.volume_slider.grid(row=0, column=2, rowspan=2, pady=20, padx=20, sticky="ns")

        # Disable interaction AFTER setting initial value
        self.volume_slider.config(state="disabled")

    def vol_up(self):
        """Increase volume by 1%, wrap around if over 100"""
        if self.current_vol < 100:
            self.current_vol += 1 
        else:
            self.current_vol = 0  # Reset volume if max is reached
        
        # Update UI
        self.volume_label.config(text=f"Volume: {self.current_vol}%")

        # Temporarily enable slider to update value
        self.volume_slider.config(state="normal")  
        self.volume_slider.set(self.current_vol)  # Sync slider with volume
        self.volume_slider.config(state="disabled")  # Re-disable after update

        # Apply volume change
        self.set_system_volume(self.current_vol)
        
    def set_system_volume(self, volume):
        """Set system volume based on the OS"""
        try:
            volume = int(volume)
            self.current_vol = volume  # Store new volume

            if platform.system() == "Windows":
                self.set_windows_volume(volume)
            elif platform.system() == "Darwin":  # macOS
                os.system(f"osascript -e 'set volume output volume {volume}'")
            elif platform.system() == "Linux":
                os.system(f"pactl set-sink-volume @DEFAULT_SINK@ {volume}%")
        except Exception as e:
            print(f"Error setting volume: {e}")

    def set_windows_volume(self, volume):
        """Set system volume in Windows using pycaw"""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_control = cast(interface, POINTER(IAudioEndpointVolume))
            volume_control.SetMasterVolumeLevelScalar(volume / 100, None)
        except Exception as e:
            print(f"Error setting Windows volume: {e}")

    def get_system_volume(self):
        """Retrieve the current system volume on startup"""
        try:
            if platform.system() == "Windows":
                return self.get_windows_volume()
            elif platform.system() == "Darwin":  # macOS
                return int(os.popen("osascript -e 'output volume of (get volume settings)'").read().strip())
            elif platform.system() == "Linux":
                return int(os.popen("pactl get-sink-volume @DEFAULT_SINK@ | awk '{print $5}' | sed 's/%//'").read().strip())
        except Exception as e:
            print(f"Error getting system volume: {e}")
            return 50  # Default if an error occurs

    def get_windows_volume(self):
        """Get the current system volume on Windows using pycaw"""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_control = cast(interface, POINTER(IAudioEndpointVolume))
            return int(volume_control.GetMasterVolumeLevelScalar() * 100)
        except Exception as e:
            print(f"Error getting Windows volume: {e}")
            return 50  # Default value

    def center_window(self, root, width=800, height=600):
        """Centers the window on the screen"""
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        root.geometry(f"{width}x{height}+{x}+{y}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BadAudioControls(root)
    root.mainloop()
