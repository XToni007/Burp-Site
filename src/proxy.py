import os
import mitmproxy.http
import logging
import random
import string

# Path to store requests and responses
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REQUESTS_DIR = os.path.join(BASE_DIR, 'requests')
RESPONSES_DIR = os.path.join(BASE_DIR, 'responses')

# Ensure directories exist
os.makedirs(REQUESTS_DIR, exist_ok=True)
os.makedirs(RESPONSES_DIR, exist_ok=True)

def generate_random_id(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def save_to_file(directory, filename, content):
    filepath = os.path.join(directory, f"{filename}.txt")
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(content)

class RequestResponseLogger:
    def request(self, flow: mitmproxy.http.HTTPFlow) -> None:
        """Log the request"""
        try:
            request_method = flow.request.method if flow.request else "UNKNOWN"
            request_path = flow.request.path if flow.request else "UNKNOWN"
            request_host = flow.request.host if flow.request else "UNKNOWN"  # Get host
            request_body = flow.request.get_text() if flow.request else ""
            
            headers = {key: value for key, value in flow.request.headers.items()}
            request_headers = "\n".join(f"{key}: {value}" for key, value in headers.items())

            random_id = generate_random_id()  # Generate random ID for this request

            # Include host in the log
            log_entry = f"{request_method} {request_path} {flow.request.http_version if flow.request else 'UNKNOWN'}\nHost: {request_host}\n{request_headers}\n\n{request_body}"
            save_to_file(REQUESTS_DIR, random_id, log_entry)
            flow.request_id = random_id  # Attach the custom ID to flow for later use
        except Exception as e:
            logging.error(f"Error logging request: {e}, flow: {flow}")

    def response(self, flow: mitmproxy.http.HTTPFlow) -> None:
        """Log the response"""
        try:
            random_id = flow.request_id  # Use the same ID from the request
            response_status = flow.response.status_code if flow.response else "UNKNOWN"
            response_headers = "\n".join(f"{key}: {value}" for key, value in flow.response.headers.items())
            response_body = flow.response.get_text() if flow.response else ""

            log_entry = f"{flow.response.http_version if flow.response else 'UNKNOWN'} {response_status}\n{response_headers}\n\n{response_body}"
            save_to_file(RESPONSES_DIR, random_id, log_entry)
        except Exception as e:
            logging.error(f"Error logging response: {e}, flow: {flow}")

# Add the addon to mitmproxy
addons = [
    RequestResponseLogger()
]