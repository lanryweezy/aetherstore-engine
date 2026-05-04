import os
import sys
import subprocess
import platform
import socket

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

try:
    from config import settings
    from database import engine
    CONFIG_LOADED = True
except ImportError:
    CONFIG_LOADED = False

def check_python():
    print(f"🐍 Python Version: {platform.python_version()}")
    return sys.version_info >= (3, 11)

def check_node():
    try:
        version = subprocess.check_output(["node", "--version"]).decode().strip()
        print(f"📦 Node.js Version: {version}")
        return True
    except:
        print("❌ Node.js not found.")
        return False

def check_directories():
    print("📂 Checking Infrastructure...")
    dirs = ["backend/ai_models", "backend/uploads", "backend/data", "backend/temp"]
    all_ok = True
    for d in dirs:
        if os.path.exists(d):
            print(f"  ✅ {d}")
        else:
            print(f"  ❌ {d} (Missing)")
            all_ok = False
    return all_ok

def check_ai_weights():
    if not CONFIG_LOADED:
        print("❌ Could not load backend config.")
        return False
        
    print("🧠 Verifying 25 AI Pillars...")
    weight_map = {
        'CLIP (Search)': settings.MODEL_PATH_CLIP,
        'ShapeR (Metric 3D)': settings.MODEL_PATH_SHAPER,
        'Boxer (Spatial)': settings.MODEL_PATH_BOXER,
        'Momentum (Kinematics)': settings.MODEL_PATH_MOMENTUM,
        'Sapiens (Pose)': settings.MODEL_PATH_SAPIENS,
        'TRIBE v2 (Neuro)': settings.MODEL_PATH_TRIBE,
        'FlowDec (Audio)': settings.MODEL_PATH_FLOWDEC,
        'SAM 2 Video': settings.MODEL_PATH_SAM2_VIDEO,
        'SAM 3 (Ultra HQ)': settings.MODEL_PATH_SAM3,
        'TactoVis (Tactile)': settings.MODEL_PATH_TACTOVIS,
        'DTC (Digital Twin)': settings.MODEL_PATH_DTC,
        'Llama 3/4 (Maverick)': settings.MODEL_PATH_MAVERICK,
    }
    
    missing_count = 0
    for name, path in weight_map.items():
        if os.path.exists(path):
            print(f"  ✅ {name.ljust(20)} [READY]")
        else:
            print(f"  ⚠️ {name.ljust(20)} [SIMULATION MODE - Weights missing at {path}]")
            missing_count += 1
    return missing_count == 0

def check_database():
    print("🗄️ Checking Database Persistence...")
    try:
        with engine.connect() as conn:
            print("  ✅ SQLite Connectivity OK")
            return True
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
        return False

def check_ports():
    print("🌐 Checking Port Availability...")
    ports = [8000, 5173, 80]
    for port in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) == 0:
                print(f"  ⚠️ Port {port} is already in use.")
            else:
                print(f"  ✅ Port {port} is available.")

def main():
    print("="*50)
    print("🩺 AETHERSTORE SYSTEM DOCTOR")
    print("="*50)
    
    status = {
        "Python 3.11+": check_python(),
        "Node.js": check_node(),
        "Infrastructure": check_directories(),
        "Database": check_database(),
        "AI Pillars": check_ai_weights()
    }
    
    check_ports()
    
    print("\n" + "="*50)
    print("📋 DIAGNOSTIC SUMMARY")
    print("="*50)
    for task, ok in status.items():
        icon = "✅" if ok else "❌"
        print(f"{icon} {task}")
    
    if all(status.values()):
        print("\n✨ SYSTEM HEALTHY: AetherStore is ready for production launch.")
    else:
        print("\n⚠️ SYSTEM DEGRADED: Some components are missing or in simulation mode.")
    print("="*50)

if __name__ == "__main__":
    main()
