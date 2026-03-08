import argparse
import atexit
import os
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
from urllib.request import urlopen
from urllib.error import URLError


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")


class ProcessManager:
    def __init__(self):
        self.processes = []

    def add(self, process):
        self.processes.append(process)

    def stop_all(self):
        for process in self.processes:
            if process.poll() is None:
                try:
                    process.terminate()
                except Exception:
                    pass

        deadline = time.time() + 4
        while time.time() < deadline:
            if all(process.poll() is not None for process in self.processes):
                return
            time.sleep(0.15)

        for process in self.processes:
            if process.poll() is None:
                try:
                    process.kill()
                except Exception:
                    pass


manager = ProcessManager()


def port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def find_free_port(start_port, end_port=8100):
    for candidate in range(start_port, end_port + 1):
        if not port_in_use(candidate):
            return candidate
    return None


def wait_for_http(url, timeout=20):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urlopen(url, timeout=1.5) as response:
                if 200 <= response.status < 500:
                    return True
        except URLError:
            pass
        except Exception:
            pass
        time.sleep(0.4)
    return False


def start_backend(host, port, reload_enabled):
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "main:app",
        "--host",
        host,
        "--port",
        str(port),
    ]
    if reload_enabled:
        cmd.append("--reload")

    process = subprocess.Popen(cmd, cwd=BACKEND_DIR)
    manager.add(process)
    return process


def stream_tunnel_output(process):
    public_url_printed = False
    while process.poll() is None:
        line = process.stdout.readline()
        if not line:
            time.sleep(0.1)
            continue

        text = line.strip()
        if not text:
            continue

        print(f"[Tunnel] {text}")

        if ("https://" in text) and ("trycloudflare.com" in text or "ngrok" in text) and not public_url_printed:
            for token in text.split():
                if token.startswith("https://") and ("trycloudflare.com" in token or "ngrok" in token):
                    print(f"\nPublic URL: {token}\n")
                    public_url_printed = True
                    break


def find_tool(tool_name):
    """Find a tool in system PATH or Python scripts directory"""
    # Try standard PATH first
    found = shutil.which(tool_name)
    if found:
        return found
    
    # Check Python scripts directory (Windows)
    if sys.platform == "win32":
        python_scripts = os.path.dirname(sys.executable)
        python_scripts_alt = os.path.join(os.path.dirname(sys.executable), "Scripts")
        
        # Also check user site-packages/Scripts (for pip install --user)
        user_base = os.environ.get("APPDATA")
        if user_base:
            user_scripts = os.path.join(user_base, "Python", "Python314", "Scripts")
            for scripts_dir in [python_scripts, python_scripts_alt, user_scripts]:
                # Try exact name first
                tool_path = os.path.join(scripts_dir, f"{tool_name}.exe")
                if os.path.exists(tool_path):
                    return tool_path
                
                # Try with -asgi suffix (for ngrok)
                if tool_name == "ngrok":
                    tool_path = os.path.join(scripts_dir, f"{tool_name}-asgi.exe")
                    if os.path.exists(tool_path):
                        return tool_path
    
    return None


def start_tunnel(frontend_port, backend_port):
    """Start ngrok tunnel using Python library"""
    try:
        from pyngrok import ngrok
        
        try:
            # Single-link mode: backend serves frontend and API together
            app_tunnel = ngrok.connect(backend_port, "http")

            app_public_url = getattr(app_tunnel, "public_url", str(app_tunnel))

            print(f"\n✅ Tunnel provider: ngrok (pyngrok)")
            print(f"🌐 App URL: {app_public_url}")
            print(f"\n🎯 SHARE THIS URL: {app_public_url}\n")
            print("=" * 60)
            print("Share this link with your teacher!")
            print("=" * 60 + "\n")
            return True
        except Exception as e:
            error_text = str(e)
            if "ERR_NGROK_108" in error_text or "simultaneous ngrok agent sessions" in error_text:
                print(f"\n⚠️  ngrok session limit reached (ERR_NGROK_108)")
                print("=" * 60)
                print("Close old ngrok sessions, then run again:")
                print("  taskkill /F /IM ngrok.exe /T")
                print("  taskkill /F /IM ngrok-asgi.exe /T")
                print()
                print("Then run:")
                print("  python run.py --tunnel")
                print("=" * 60 + "\n")
            elif "authentication failed" in error_text or "authtoken" in error_text:
                print(f"\n⚠️  ngrok requires a free authtoken to work")
                print("=" * 60)
                print("Option 1: Set up ngrok authtoken")
                print("  1. Sign up: https://dashboard.ngrok.com/signup")
                print("  2. Get authtoken: https://dashboard.ngrok.com/get-started/your-authtoken")
                print("  3. Run: ngrok config add-authtoken YOUR_TOKEN")
                print("  4. Try again: python run.py --tunnel")
                print()
                print("Option 2: Use local network IP (same network only)")
                print(f"  - Your CipherX is available at: http://YOUR_IP:{frontend_port}")
                print("  - Find your IP: run 'ipconfig' and look for IPv4 Address")
                print("=" * 60 + "\n")
            else:
                print(f"Failed to start ngrok tunnel: {e}")
            return False
    except ImportError:
        pass
    
    # Try cloudflared
    cloudflared = find_tool("cloudflared")
    if cloudflared:
        cmd = [cloudflared, "tunnel", "--url", f"http://127.0.0.1:{backend_port}", "--no-autoupdate"]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=ROOT_DIR,
        )
        manager.add(process)
        threading.Thread(target=stream_tunnel_output, args=(process,), daemon=True).start()
        print("Tunnel provider: cloudflared (Cloudflare Tunnel)")
        return True

    # Try ngrok CLI
    ngrok = find_tool("ngrok")
    if ngrok:
        cmd = [ngrok, "http", str(backend_port)]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=ROOT_DIR,
        )
        manager.add(process)
        threading.Thread(target=stream_tunnel_output, args=(process,), daemon=True).start()
        print("Tunnel provider: ngrok (CLI)")
        print("Generating public URL...")
        return True

    print("\n⚠️  No tunnel provider available")
    print("=" * 60)
    print("To share CipherX with your teacher:")
    print()
    print("Option 1: Local Network (Recommended for same network)")
    print(f"  Share your IP: http://YOUR_IP:{backend_port}")
    print("  Find IP: Run 'ipconfig' in terminal (look for IPv4 Address)")
    print()
    print("Option 2: Public Link via ngrok (Recommended for remote)")
    print("  1. Install: pip install pyngrok")
    print("  2. Sign up: https://dashboard.ngrok.com/signup")
    print("  3. Get token: https://dashboard.ngrok.com/get-started/your-authtoken")
    print("  4. Configure: ngrok config add-authtoken YOUR_TOKEN")
    print("  5. Run: python run.py --tunnel")
    print("=" * 60 + "\n")
    return False


def handle_exit(*_):
    manager.stop_all()


def main():
    parser = argparse.ArgumentParser(description="CipherX one-command runner")
    parser.add_argument("--backend-port", type=int, default=8000)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--reload", action="store_true", help="Enable backend auto-reload")
    parser.add_argument("--tunnel", action="store_true", help="Expose app with cloudflared/ngrok")
    args = parser.parse_args()

    if not os.path.exists(os.path.join(BACKEND_DIR, "main.py")):
        print("Error: backend/main.py not found.")
        return 1

    backend_port = args.backend_port
    if port_in_use(backend_port):
        fallback = find_free_port(backend_port + 1, 8100)
        if fallback is None:
            print(f"Error: backend port {backend_port} is in use and no free fallback port found.")
            return 1
        print(f"Warning: backend port {backend_port} is busy. Using {fallback} instead.")
        backend_port = fallback

    atexit.register(handle_exit)
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    print("Starting CipherX...")
    print(f"App:  http://{args.host}:{backend_port}")

    backend = start_backend(args.host, backend_port, args.reload)

    backend_ok = wait_for_http(f"http://{args.host}:{backend_port}/")

    if not backend_ok:
        print("\nStartup check failed.")
        if backend.poll() is not None:
            print("Backend exited unexpectedly.")
        handle_exit()
        return 1

    app_url = f"http://{args.host}:{backend_port}"

    print("\nCipherX is running.")
    print(f"Open: {app_url}")

    if args.tunnel:
        print("\nStarting tunnel for app...")
        start_tunnel(backend_port, backend_port)

    print("Press Ctrl+C to stop all services.")

    try:
        while True:
            if backend.poll() is not None:
                print("\nBackend process stopped.")
                break
            time.sleep(0.5)
    finally:
        handle_exit()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
