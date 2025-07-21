MultiCam VR OBS Switcher
=========================
Auto‑toggle your OBS camera sources (“Front Camera” / “Back Camera”) based on your VR headset’s yaw.

Prerequisites
-------------
• Windows OS  
• Python 3.8 or higher  
• OBS Studio with obs‑websocket v5+ installed  
• SteamVR running

Installation
------------
1. Open Command Prompt (Win+R → “cmd” → Enter).  
2. Navigate to the project folder:
   cd C:\Users\techg\obs-vr-switcher\MultiCamVR
3. Install dependencies:
   pip install psutil openvr obsws-python

Usage
-----
1. In OBS, name two sources exactly “Front Camera” and “Back Camera.”  
2. Run the script:
   python vr_obs_switcher.py --front-source "Front Camera" --back-source "Back Camera" --ip 127.0.0.1 --port 4455
3. Look straight ahead in your headset and press Enter to zero your yaw.  
4. Turn your head left/right—the script will swap sources in OBS automatically.

Command‑line options
--------------------
--front-source   Name of the forward-facing camera source  
--back-source    Name of the backward-facing camera source  
--ip             OBS WebSocket server IP (default: 127.0.0.1)  
--port           OBS WebSocket port (default: 4455)  
--password       OBS WebSocket password (if set)

Troubleshooting
---------------
• “Unable to connect to OBS” → Check WebSocket port/password in OBS Settings → WebSockets.  
• “Module not found” → Re-run pip install.  
• Camera names don’t match? → Rename in OBS or use flags.

Support
-------
Report issues or suggest features:  
https://github.com/<your-username>/vr-obs-switcher/issues

Enjoy your VR‑powered camera switching!
