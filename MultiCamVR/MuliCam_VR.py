#!/usr/bin/env python3
"""
VR OBS Switcher v2.1
--------------------

Auto-toggles your OBS front/back camera sources based on HMD yaw.

Usage (CMD):
    py .\vr_obs_switcher.py --front-source "Front Camera" --back-source "Back Camera" --ip 127.0.0.1 --port 4455
"""

import time, math, argparse, psutil, openvr
import obsws_python as obs

# —— Defaults —— #
DEFAULT_FRONT   = "Front Camera"
DEFAULT_BACK    = "Back Camera"
DEFAULT_THRESH  = 30.0
DEFAULT_INTV    = 0.1
REQUIRED_PROCS  = ["obs64.exe", "vrserver.exe"]


def wait_for_services():
    print("[AUTO] Waiting for OBS & SteamVR…")
    while True: 
        procs = {p.name().lower() for p in psutil.process_iter()}
        if all(req in procs for req in REQUIRED_PROCS):
            print("[AUTO] All required services are up.")
            return
        time.sleep(1)


def find_hmd_index(vr_sys):
    for i in range(openvr.k_unMaxTrackedDeviceCount):
        if vr_sys.getTrackedDeviceClass(i) == openvr.TrackedDeviceClass_HMD:
            print(f"[INFO] Found HMD at device index {i}")
            return i
    raise RuntimeError("No HMD device found")


def get_yaw_from_pose(pose):
    m = pose.mDeviceToAbsoluteTracking
    m00, m11, m22 = m[0][0], m[1][1], m[2][2]
    qw = math.sqrt(max(0, 1 + m00 + m11 + m22)) / 2
    qx = math.copysign(math.sqrt(max(0, 1 + m00 - m11 - m22)) / 2, m[2][1] - m[1][2])
    qy = math.copysign(math.sqrt(max(0, 1 - m00 + m11 - m22)) / 2, m[0][2] - m[2][0])
    qz = math.copysign(math.sqrt(max(0, 1 - m00 - m11 + m22)) / 2, m[1][0] - m[0][1])
    return math.degrees(math.atan2(2*(qw*qz + qx*qy), 1 - 2*(qy*qy + qz*qz)))


def show_source(ws, scene, show_name, hide_name):
    """
    Within the given scene, show `show_name` and hide `hide_name`.
    """
    try:
        # 1) list all items in the scene
        resp = ws.get_scene_item_list(name=scene)
        # resp.scene_items is a list of dicts with keys "sceneItemId" and "sourceName"
        for item in resp.scene_items:
            sid = item["sceneItemId"]
            src = item["sourceName"]
            if   src == show_name:
                ws.set_scene_item_enabled(
                    scene_name=scene,
                    item_id=sid,
                    enabled=True
                )
            elif src == hide_name:
                ws.set_scene_item_enabled(
                    scene_name=scene,
                    item_id=sid,
                    enabled=False
                )        
        print(f"[DEBUG] Toggled '{show_name}' visible and '{hide_name}' hidden")
    except Exception as e:
        print(f"[ERROR] Failed to switch sources: {e}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--front-source", default=DEFAULT_FRONT)
    p.add_argument("--back-source",  default=DEFAULT_BACK)
    p.add_argument("--threshold",    type=float, default=DEFAULT_THRESH)
    p.add_argument("--interval",     type=float, default=DEFAULT_INTV)
    p.add_argument("--ip",           default="localhost")
    p.add_argument("--port",         type=int,   default=4455)
    p.add_argument("--password",     default="")
    args = p.parse_args()

    wait_for_services()

    # —— Init OpenVR —— #
    print("[INIT] Initializing OpenVR…")
    openvr.init(openvr.VRApplication_Background)
    vr_sys  = openvr.VRSystem()
    hmd_index = find_hmd_index(vr_sys)
    # Instead of connect_obs()
    print(f"[INIT] Connecting to OBS v5 WebSocket at {args.ip}:{args.port}…")
    ws = obs.ReqClient(host=args.ip, port=args.port, password=args.password)


    # —— Connect OBS & grab scene —— #
    print(f"[INIT] Connecting to OBS v5 WebSocket at {args.ip}:{args.port}…")
    ws = obs.ReqClient(host=args.ip, port=args.port, password=args.password)
    # fetch the active scene via the v5 client method
    resp  = ws.get_current_program_scene()
    scene = resp.current_program_scene_name
    print(f"[INIT] Using scene: {scene!r}")

    # —— Calibrate zero yaw —— #
    print("[CALIB] Look straight ahead and hit Enter to zero yaw.")
    input()
    poses    = vr_sys.getDeviceToAbsoluteTrackingPose(
                  openvr.TrackingUniverseStanding, 0,
                  openvr.k_unMaxTrackedDeviceCount
              )
    zero_yaw = get_yaw_from_pose(poses[hmd_index])
    print(f"[CALIB] Zero yaw = {zero_yaw:.1f}°")

    # —— Main loop —— #
    print("[RUN] Entering main loop… (Ctrl+C to exit)")
    current = None
    try:
        while True:
            poses = vr_sys.getDeviceToAbsoluteTrackingPose(
                        openvr.TrackingUniverseStanding, 0,
                        openvr.k_unMaxTrackedDeviceCount
                    )
            pose = poses[hmd_index]

            # skip if tracking is invalid
            if not pose.bPoseIsValid:
                time.sleep(args.interval)
                continue

            yaw = get_yaw_from_pose(pose) - zero_yaw
            yaw = (yaw + 180) % 360 - 180      # wrap to –180…180

            face_front = abs(yaw) <= args.threshold
            target     = args.front_source if face_front else args.back_source
            other      = args.back_source  if face_front else args.front_source

            if target != current:
                print(f"[RUN] yaw={yaw:.1f}° → show={target}, hide={other}")
                show_source(ws, scene, target, other)
                current = target

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\n[EXIT] User aborted, cleaning up…")
    finally:
        ws.disconnect()
        openvr.shutdown()



if __name__ == "__main__":
    main()
