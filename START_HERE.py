#!/usr/bin/env python3
"""
CipherX Pro - Startup Manager
Smart Cleanup: Only kills processes on Port 8000 to prevent self-termination.
"""

import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path

# Root directory of the project
root_dir = Path(__file__).resolve().parent
backend_dir = root_dir / "backend"

def print_header():
    """Print startup header"""
    print("\n" + "="*60)
    print("      CipherX Pro - AI-Powered Universal Decoder")
    print("="*60 + "\n")

def check_dependencies():
    """Check if required packages are installed"""
    print("[1/4] Checking dependencies...")
    try:
        import fastapi
        import uvicorn
        print("+ Dependencies confirmed")
        return True
    except ImportError:
        print("! Installing missing dependencies (FastAPI, Uvicorn)...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "pydantic"],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("+ Dependencies installed")
            return True
        except:
            print("! Warning: Automatic installation failed. Attempting to continue...")
            return True

def kill_existing_servers():
    """Only kill processes listening on Port 8000 to avoid killing this script"""
    print("[2/4] Liberating Port 8000 (Cleaning up old servers)...")
    if sys.platform == "win32":
        try:
            # Find PID listening on port 8000
            result = subprocess.run(["netstat", "-ano", "-p", "tcp"], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if ":8000" in line and "LISTENING" in line:
                    pid = line.strip().split()[-1]
                    if pid != "0":
                        print(f"  - Found old server (PID: {pid}). Killing it...")
                        subprocess.run(["taskkill", "/F", "/PID", pid, "/T"], 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        time.sleep(1)
        except Exception as e:
            # Fallback for older systems
            pass
    print("+ Environment ready")

def start_server():
    """Start the backend server in a NEW window"""
    print("[3/4] Launching CipherX Server...")
    
    main_py = backend_dir / "main.py"
    if not main_py.exists():
        print(f"Error: {main_py} not found!")
        return None
    
    try:
        # Start uvicorn in a NEW window so it doesn't block this script
        # Using --reload flag so any backend Python changes apply instantly
        creation_flags = subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            cwd=str(backend_dir),
            creationflags=creation_flags
        )
        
        # Verify server is up
        print("  - Waiting for server to initialize...", end="", flush=True)
        for i in range(10):
            print(".", end="", flush=True)
            time.sleep(1)
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            if sock.connect_ex(('127.0.0.1', 8000)) == 0:
                sock.close()
                print("\n+ Server is LIVE at http://127.0.0.1:8000")
                return process
            sock.close()
        
        print("\n! Server taking longer than expected to respond...")
        return process
    except Exception as e:
        print(f"\nError: {e}")
        return None

def open_browser():
    """Open the web interface"""
    print("[4/4] Opening User Interface...")
    try:
        time.sleep(0.5)
        webbrowser.open("http://127.0.0.1:8000")
        print("+ Browser opened successfully")
    except:
        print("! Please open manually: http://127.0.0.1:8000")

def main():
    if sys.platform == "win32": os.system('color')
    print_header()
    check_dependencies()
    kill_existing_servers()
    process = start_server()
    if not process:
        print("Fatal: Could not initialize server.")
        input("Press Enter to exit...")
        return 1
    
    open_browser()
    print("\n" + "="*60)
    print(" 🎉 CipherX Pro is Running!")
    print("="*60)
    print("Local URL: http://127.0.0.1:8000")
    print("\nKeep this window open. Close the server window to stop.")
    print("="*60 + "\n")
    
    try:
        # Keep managing the process
        while True:
            if process.poll() is not None: 
                print("! Backend server process has closed.")
                break
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nStopping...")
        process.terminate()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Fatal unhandled error: {e}")
        input("Press Enter to exit...")
