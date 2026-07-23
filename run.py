"""
ForensicDB Entry Point
Runs full automated check and launches application server.
"""
from start import print_banner, ensure_dependencies, setup_database, open_browser, run_application
import threading

if __name__ == '__main__':
    print_banner()
    ensure_dependencies()
    setup_database()
    threading.Thread(target=open_browser, daemon=True).start()
    run_application()
