# MultiCam VR OBS Switcher

**Auto‑toggle your OBS “Front Camera” / “Back Camera” sources based on VR headset yaw.**

## 🚀 Prerequisites

- **Windows**  
- **Python 3.8+**  
- **OBS Studio** with [obs‑websocket v5+](https://github.com/obsproject/obs-websocket)  
- **SteamVR** running

## 🔧 Installation

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/vr-obs-switcher.git
cd vr-obs-switcher/MultiCamVR

# 2. Install Python deps
pip install psutil openvr obsws-python
