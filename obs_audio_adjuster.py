from obsws_python import ReqClient  # Use ReqClient to interact with OBS
import time

try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
except ImportError:
    print("Warning: pycaw module not found. Install it with `pip install pycaw comtypes` on Windows.")

class ObsAudioAdjuster:
    
    def __init__(self):
        # OBS WebSocket settings
        self.OBS_HOST = "localhost"
        self.OBS_PORT = 4456
        self.OBS_PASSWORD = "yTUWLOXU5s1epKDO"  # Ensure this matches OBS settings

        try:
            # Connect to OBS WebSocket
            self.obs = ReqClient(host=self.OBS_HOST, port=self.OBS_PORT, password=self.OBS_PASSWORD)
            print("✅ Connected to OBS WebSocket")
        except Exception as e:
            print(f"❌ Error connecting to OBS: {e}")
            self.obs = None

    def get_audio_volume(self, source_name):
        """Gets the current volume level of an OBS audio source."""
        if not self.obs:
            print("❌ OBS is not connected!")
            return None
        try:
            response = self.obs.get_input_volume(source_name)
            return response.input_volume_db  # Returns volume in decibels
        except Exception as e:
            print(f"❌ Error getting OBS volume: {e}")
            return None

   

    def set_audio_volume(self, source_name, volume_db):
        """Sets the volume of an OBS audio source in decibels (dB) by converting it to a valid multiplier."""
        if not self.obs:
            print("❌ OBS is not connected!")
            return
        
        try:
            # Convert dB to a multiplier (OBS requires a linear scale)
            volume_mul = 10 ** (volume_db / 20)
            volume_mul = max(0.0, min(1.0, volume_mul))  # Ensure it stays within valid range

            self.obs.set_input_volume(source_name, volume_mul)  # Use multiplier
            print(f"🔊 Volume of '{source_name}' set to {volume_db} dB (Multiplier: {volume_mul:.3f}) in OBS")
        except Exception as e:
            print(f"❌ Error setting OBS volume: {e}")



    def get_windows_volume(self):
        """Get the current system volume on Windows using pycaw"""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_control = cast(interface, POINTER(IAudioEndpointVolume))
            return int(volume_control.GetMasterVolumeLevelScalar() * 100)  # Convert to percentage
        except Exception as e:
            print(f"❌ Error getting Windows volume: {e}")
            return 50  # Default to 50% if there's an error

    def set_windows_volume(self, volume):
        """Set system volume in Windows using pycaw"""
        try:
            volume = max(0, min(100, volume))  # Ensure volume is between 0-100%
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_control = cast(interface, POINTER(IAudioEndpointVolume))
            volume_control.SetMasterVolumeLevelScalar(volume / 100, None)
            print(f"🔊 System volume set to {volume}%")
        except Exception as e:
            print(f"❌ Error setting Windows volume: {e}")

    def adjust_obs_volume_based_on_system(self, audio_source):
        """Continuously checks system volume and adjusts OBS audio volume accordingly."""
        print("🎵 Starting OBS volume adjustment based on system volume...")
        try:
            while True:
                system_volume = self.get_windows_volume()
                print(f"🎚 System Volume: {system_volume}%")

                # Convert system volume to an appropriate OBS dB value
                if system_volume > 95:
                    obs_volume_db = 0  # Max OBS volume
                elif system_volume > 90:
                    obs_volume_db = -2
                elif system_volume > 85:
                    obs_volume_db = -4
                elif system_volume > 80:
                    obs_volume_db = -6
                elif system_volume > 75:
                    obs_volume_db = -8
                elif system_volume > 70:
                    obs_volume_db = -10
                elif system_volume > 65:
                    obs_volume_db = -12
                elif system_volume > 60:
                    obs_volume_db = -14
                elif system_volume > 55:
                    obs_volume_db = -16
                elif system_volume > 50:
                    obs_volume_db = -18
                elif system_volume > 40:
                    obs_volume_db = -20
                elif system_volume > 30:
                    obs_volume_db = -25
                elif system_volume > 20:
                    obs_volume_db = -30
                elif system_volume > 10:
                    obs_volume_db = -35
                else:
                    obs_volume_db = -40  # Lowest OBS volume


                print(f"🔊 Adjusting OBS '{audio_source}' to {obs_volume_db} dB")
                self.set_audio_volume(audio_source, obs_volume_db)

                time.sleep(.5)  # Check every 5 seconds
        except KeyboardInterrupt:
            print("🛑 Stopping OBS audio adjuster...")
            self.disconnect()

    def disconnect(self):
        """Disconnect from OBS WebSocket."""
        if self.obs:
            self.obs.disconnect()
            print("🔌 Disconnected from OBS WebSocket")


# Running script
if __name__ == "__main__":
    obs_adjuster = ObsAudioAdjuster()
    obs_adjuster.adjust_obs_volume_based_on_system("Desktop Audio")  # Adjust OBS source volume dynamically
