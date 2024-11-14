# import threading
# import subprocess
# from utils import save_to_file, read_file  # Menggunakan path penuh ke utils.py

# def run_flask():
#     from app import app
#     app.run(host="0.0.0.0", port=5000)

# def run_mitmproxy():
#     subprocess.run(["mitmdump", "-s", "proxy.py"])

# if __name__ == "__main__":
#     flask_thread = threading.Thread(target=run_flask)
#     mitmproxy_thread = threading.Thread(target=run_mitmproxy)

#     flask_thread.start()
#     mitmproxy_thread.start()

#     flask_thread.join()
#     mitmproxy_thread.join()

import threading
import subprocess
import logging
from utils import save_to_file, read_file  # Path penuh ke utils.py

logging.basicConfig(level=logging.INFO)

def run_flask():
    from app import app
    app.run(host="0.0.0.0", port=5000)

def run_mitmproxy():
    try:
        subprocess.run(["mitmdump", "-s", "/app/src/proxy.py", "--listen-host", "0.0.0.0", "--listen-port", "8080"], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to start mitmdump: {e}")

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    mitmproxy_thread = threading.Thread(target=run_mitmproxy)

    flask_thread.start()
    mitmproxy_thread.start()

    flask_thread.join()
    mitmproxy_thread.join()
