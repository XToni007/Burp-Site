import os
import logging
import requests
import re
from flask import Flask, render_template, jsonify, redirect, url_for, request as flask_request
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

app = Flask(__name__)
socketio = SocketIO(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Absolute paths to request and response directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REQUESTS_DIR = os.path.join(BASE_DIR, 'requests')
RESPONSES_DIR = os.path.join(BASE_DIR, 'responses')
REPEATER_DIR = os.path.join(BASE_DIR, 'repeater_requests')
INTRUDER_DIR = os.path.join(BASE_DIR, 'intruder_requests')
PAYLOAD_DIR = os.path.join(BASE_DIR, 'payloads')

# Ensure directories exist
os.makedirs(REPEATER_DIR, exist_ok=True)
os.makedirs(INTRUDER_DIR, exist_ok=True)
os.makedirs(PAYLOAD_DIR, exist_ok=True)

def clean_request_template(request_template):
    """Remove unnecessary newlines from the request template."""
    cleaned_lines = [line for line in request_template.splitlines() if line.strip()]
    return "\n".join(cleaned_lines)

def sanitize_host_for_parsing(request_data, keep_marking_symbols=False):
    """Replace marked host with a temporary placeholder to allow proper parsing."""
    if "§" in request_data and not keep_marking_symbols:
        # Replace `§marked§` with `marked` temporarily for parsing
        request_data = request_data.replace("§", "")

    # Tambahkan validasi tambahan
    if "Host: " not in request_data or request_data.split("Host: ")[1].strip() == "":
        logging.error("Invalid or missing Host header in request data.")
        raise ValueError("Invalid Host header detected.")

    return request_data

def parse_http_request(request_data):
    """Parse the full HTTP request data. Returns the method, path, headers, body, host, and protocol."""
    lines = request_data.strip().splitlines()
    method, path, protocol = "UNKNOWN", "UNKNOWN", "HTTP/1.1"
    host = None
    headers = {}
    body = []
    in_headers = True

    for i, line in enumerate(lines):
        if i == 0:
            parts = line.split()
            if len(parts) >= 3:
                method, path, protocol = parts[0], parts[1], parts[2]
        elif in_headers:
            if line.lower().startswith("host:"):
                host = line.split(":", 1)[1].strip()
            elif ": " in line:
                key, value = line.split(": ", 1)
                headers[key] = value.strip()
            elif line == "":
                in_headers = False
        else:
            body.append(line)

    body_str = "\n".join(body)
    logging.debug(f"Parsed HTTP Request: method={method}, path={path}, host={host}, protocol={protocol}")
    return method, path, host, headers, body_str, protocol

def parse_http_response(response_data):
    """Parse the HTTP response data. Returns the status code."""
    lines = response_data.splitlines()
    if lines:
        status_line = lines[0].strip()
        parts = status_line.split()
        if len(parts) >= 2:
            return parts[1]  # Return status code
    logging.debug(f"Parsed HTTP Response: status={parts[1] if len(parts) >= 2 else 'N/A'}")
    return parts[1] if len(parts) >= 2 else "N/A"


def read_file(directory, flow_id):
    filepath = os.path.join(directory, f"{flow_id}.txt")
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as file:
                logging.debug(f"Reading file from {filepath}")
                return file.read()
        else:
            logging.error(f"File {filepath} does not exist.")
    except Exception as e:
        logging.error(f"Error reading file {filepath}: {e}")
    return None

def save_to_file(directory, flow_id, content):
    filepath = os.path.join(directory, f"{flow_id}.txt")
    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)
        logging.debug(f"File saved successfully at {filepath}")
    except Exception as e:
        logging.error(f"Error writing to file {filepath}: {e}")

def replace_targets_with_payloads(template, payload):
    """Replace all marked placeholders in the template with the actual payload."""
    # Replace marked placeholders
    return re.sub(r"§.+?§", payload, template)

def save_configuration_with_marked_parameters(request_template, flow_id):
    """Ensure marked parameters are saved correctly."""
    save_to_file(INTRUDER_DIR, flow_id, request_template)

def prepare_request_for_sending(template):
    """Remove marking symbols before sending the request and log cleaned data."""
    # Clean up any remaining marking symbols
    cleaned_template = template.replace("§", "")
    logging.debug(f"Cleaned Request before sending: {cleaned_template}")
    return cleaned_template

@app.route("/", methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/http-history')
def http_history():
    requests_data = []
    try:
        request_files = [f for f in os.listdir(REQUESTS_DIR) if f.endswith('.txt')]
        for file in request_files:
            flow_id = file.split('.')[0]
            request_data = read_file(REQUESTS_DIR, flow_id)
            response_data = read_file(RESPONSES_DIR, flow_id)

            if request_data and response_data:
                method, url, host, _, _, protocol = parse_http_request(request_data)
                status = parse_http_response(response_data)
            else:
                method, url, host, status, protocol = "UNKNOWN", "UNKNOWN", "UNKNOWN", "N/A", "HTTP/1.1"

            requests_data.append({
                'flow_id': flow_id,
                'method': method,
                'url': url,
                'host': host,
                'status': status,
                'protocol': protocol
            })
    except Exception as e:
        logging.error(f"Error in http_history: {e}")
    return render_template('http_history.html', requests=requests_data)

# WebSocket event untuk mengirim data HTTP history ke klien
@socketio.on('get_http_history')
def send_http_history():
    requests_data = []
    try:
        request_files = [f for f in os.listdir(REQUESTS_DIR) if f.endswith('.txt')]
        for file in request_files:
            flow_id = file.split('.')[0]
            request_data = read_file(REQUESTS_DIR, flow_id)
            response_data = read_file(RESPONSES_DIR, flow_id)

            if request_data and response_data:
                method, url, host, _, _, protocol = parse_http_request(request_data)
                status = parse_http_response(response_data)
            else:
                method, url, host, status, protocol = "UNKNOWN", "UNKNOWN", "UNKNOWN", "N/A", "HTTP/1.1"

            requests_data.append({
                'flow_id': flow_id,
                'method': method,
                'url': url,
                'host': host,
                'status': status,
                'protocol': protocol
            })
        emit('http_history_data', requests_data)  # Kirim data ke klien
    except Exception as e:
        logging.error(f"Error in send_http_history: {e}")

@app.route('/http-history/details/<flow_id>', methods=['GET'])
def http_history_details(flow_id):
    """Endpoint to show details of a specific HTTP request and response."""
    request_data = read_file(REQUESTS_DIR, flow_id)
    response_data = read_file(RESPONSES_DIR, flow_id)

    if request_data and response_data:
        return jsonify({
            'request': request_data,
            'response': response_data
        })
    else:
        return jsonify({'error': f'Request or Response file not found for flow_id: {flow_id}'}), 404

@app.route('/http-history/clear', methods=['POST'])
def clear_http_history():
    """Clear all request and response files in HTTP history."""
    try:
        # Hapus semua file di folder requests
        for filename in os.listdir(REQUESTS_DIR):
            file_path = os.path.join(REQUESTS_DIR, filename)
            os.remove(file_path)
        
        # Hapus semua file di folder responses
        for filename in os.listdir(RESPONSES_DIR):
            file_path = os.path.join(RESPONSES_DIR, filename)
            os.remove(file_path)

        logging.info("HTTP history cleared successfully.")
        return redirect(url_for('http_history'))
    except Exception as e:
        logging.error(f"Error clearing HTTP history: {e}")
        return jsonify({'error': 'Failed to clear HTTP history'}), 500

@app.route('/send-to-repeater/<flow_id>')
def send_to_repeater(flow_id):
    """Endpoint to send a specific request to the repeater."""
    try:
        # Pastikan file request ada
        request_data = read_file(REQUESTS_DIR, flow_id)
        if not request_data:
            return jsonify({'error': f'Request file not found for flow_id: {flow_id}'}), 404

        # Simpan ke direktori Repeater
        save_to_file(REPEATER_DIR, flow_id, request_data)
        logging.info(f"Request {flow_id} successfully sent to Repeater.")
        return redirect(url_for('repeater'))
    except Exception as e:
        logging.error(f"Error in send_to_repeater for flow_id {flow_id}: {e}")
        return jsonify({'error': 'Failed to send request to Repeater.'}), 500

@app.route('/send-to-intruder/<flow_id>')
def send_to_intruder(flow_id):
    """Endpoint to send a specific request to the Intruder."""
    try:
        # Pastikan file request ada
        request_data = read_file(REQUESTS_DIR, flow_id)
        if not request_data:
            return jsonify({'error': f'Request file not found for flow_id: {flow_id}'}), 404

        # Simpan ke direktori Intruder
        save_to_file(INTRUDER_DIR, flow_id, request_data)
        logging.info(f"Request {flow_id} successfully sent to Intruder.")
        return redirect(url_for('intruder'))
    except Exception as e:
        logging.error(f"Error in send_to_intruder for flow_id {flow_id}: {e}")
        return jsonify({'error': 'Failed to send request to Intruder.'}), 500

@app.route('/repeater')
def repeater():
    """Endpoint for the Repeater page."""
    repeater_files = [f for f in os.listdir(REPEATER_DIR) if f.endswith('.txt')]
    requests_data = []

    for file in repeater_files:
        flow_id = file.split('.')[0]  # Remove file extension
        request_data = read_file(REPEATER_DIR, flow_id)
        if request_data:
            method, path, host, headers, body, protocol = parse_http_request(request_data)
            requests_data.append({
                'flow_id': flow_id,
                'method': method,
                'path': path,
                'host': host
            })

    return render_template('repeater.html', requests=requests_data)

@app.route('/repeater/request/<flow_id>')
def get_repeater_request(flow_id):
    """Get the details of a specific request for the Repeater feature."""
    request_data = read_file(REPEATER_DIR, flow_id)
    if request_data:
        method, path, host, headers, body, protocol = parse_http_request(request_data)
        return jsonify({
            'method': method,
            'path': path,
            'host': host,
            'headers': headers,
            'body': body,
            'protocol': protocol
        })
    return jsonify({'error': 'Request not found'}), 404

@app.route('/repeater/save/<flow_id>', methods=['POST'])
def save_repeater_request(flow_id):
    """Save a modified request in the Repeater feature."""
    data = flask_request.json

    # Extract data from the request payload
    method = data.get('method', 'GET').upper()
    path = data.get('path', '/')
    host = data.get('host', '')
    headers = data.get('headers', {})
    body = data.get('body', '')
    protocol = data.get('protocol', 'HTTP/1.1')

    # Construct the HTTP request template
    request_template = f"{method} {path} {protocol}\n"
    request_template += f"Host: {host}\n"
    for header_name, header_value in headers.items():
        request_template += f"{header_name}: {header_value}\n"
    request_template += "\n"  # Separate headers from body
    request_template += body

    # Save the request template to the REPEATER_DIR
    save_to_file(REPEATER_DIR, flow_id, request_template)
    logging.info(f"Request saved to repeater with flow_id: {flow_id}")
    
    return jsonify({'message': 'Request saved successfully'}), 200

@app.route('/repeater/send', methods=['POST'])
def send_repeater_request():
    """Send a modified request from the Repeater feature."""
    data = flask_request.json
    url = f"{'https' if flask_request.is_secure else 'http'}://{data['host']}{data['path']}"
    headers = data.get('headers', {})
    method = data.get('method', 'GET').upper()
    body = data.get('body', '')

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            data=body
        )

        response_data = {
            "status": response.status_code,
            "headers": dict(response.headers),
            "body": response.text
        }
        return jsonify(response_data)
    except Exception as e:
        logging.error(f"Error sending repeater request: {e}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/repeater/clear', methods=['POST'])
def clear_repeater():
    """Clear all request and response files in Repeater."""
    try:
        # Hapus semua file di folder requests
        for filename in os.listdir(REPEATER_DIR):
            file_path = os.path.join(REPEATER_DIR, filename)
            os.remove(file_path)

        logging.info("Repater History cleared successfully.")
        return redirect(url_for('repeater'))
    except Exception as e:
        logging.error(f"Error clearing Repeater history: {e}")
        return jsonify({'error': 'Failed to clear Repeater history'}), 500

@app.route('/intruder')
def intruder():
    """Endpoint for the Intruder page."""
    intruder_files = [f for f in os.listdir(INTRUDER_DIR) if f.endswith('.txt')]
    requests_data = []

    for file in intruder_files:
        flow_id = file.split('.')[0]  # Remove file extension
        request_data = read_file(INTRUDER_DIR, flow_id)
        if request_data:
            method, path, host, headers, body, protocol = parse_http_request(request_data)
            requests_data.append({
                'flow_id': flow_id,
                'method': method,
                'path': path,
                'host': host,
                'protocol': protocol
            })

    return render_template('intruder.html', requests=requests_data)

@app.route('/intruder/request/<flow_id>')
def get_intruder_request(flow_id):
    """Get the details of a specific request for the Intruder feature."""
    request_data = read_file(INTRUDER_DIR, flow_id)
    if request_data:
        method, path, host, headers, body, protocol = parse_http_request(request_data)
        return jsonify({
            'method': method,
            'path': path,
            'host': host,
            'headers': headers,
            'body': body,
            'protocol': protocol
        })
    return jsonify({'error': 'Request not found'}), 404

@app.route('/intruder/configure/<flow_id>', methods=['GET', 'POST'])
def configure_intruder(flow_id):
    """Configure the Intruder attack for a specific request."""
    if flask_request.method == 'POST':
        request_data = flask_request.form.get('request')
        wordlist = flask_request.files.get('wordlist')

        # Use duplicated request file in `INTRUDER_DIR`
        intruder_flow_id = f"{flow_id}"

        if request_data:
            logging.debug(f"Saving request template before processing: {request_data}")

            # Jangan sanitize simbol saat menyimpan
            sanitized_request = sanitize_host_for_parsing(request_data, keep_marking_symbols=True)

            # Validasi bahwa template masih memiliki Host yang valid
            if not "Host: " in sanitized_request or sanitized_request.split("Host: ")[1].strip() == "":
                logging.error("Invalid Host detected. Please check your request template.")
                return jsonify({'error': 'Invalid Host in request template.'}), 400

            # Bersihkan karakter newline yang tidak perlu sebelum menyimpan menggunakan fungsi yang sudah ada
            sanitized_request = clean_request_template(sanitized_request)

            # Simpan template yang sudah ditandai parameter
            save_configuration_with_marked_parameters(sanitized_request, intruder_flow_id)
            logging.debug(f"Request template after saving: {sanitized_request}")

        if wordlist:
            # Save wordlist file if uploaded
            filename = secure_filename("wordlist.txt")  # Save as a standard name
            filepath = os.path.join(PAYLOAD_DIR, filename)
            wordlist.save(filepath)
        # Redirect after successful configuration
        return render_template('configure_intruder.html', flow_id=flow_id)

    # Handle GET request - load existing request template
    intruder_flow_id = f"{flow_id}"
    request_data = read_file(INTRUDER_DIR, intruder_flow_id)
    if request_data:
        # Parse using sanitized request
        sanitized_request = sanitize_host_for_parsing(request_data)
        method, path, host, headers, body, protocol = parse_http_request(sanitized_request)
        return render_template(
            'configure_intruder.html',
            flow_id=intruder_flow_id,
            method=method,
            path=path,
            host=host,
            headers=headers,
            body=body,
            protocol=protocol,
            request_content=request_data
        )

    logging.error(f"Request file not found for flow_id: {intruder_flow_id}")
    return jsonify({'error': 'Request not found'}), 404

@app.route('/intruder/run', methods=['POST'])
def run_bruteforce_attack():
    """Run the Intruder feature, sending requests with payloads to marked targets."""
    data = flask_request.json
    flow_id = data.get('flow_id')
    payloads = read_file(PAYLOAD_DIR, 'wordlist')
    if payloads:
        payloads = payloads.splitlines()  # Ubah isi file menjadi list
    else:
        logging.error('Wordlist file not found or empty.')
        return jsonify({'error': 'Wordlist file not found or empty'}), 404
    
    request_template = read_file(INTRUDER_DIR, flow_id)
    
    if not request_template:
        return jsonify({'error': 'Request template not found'}), 404

    # # Check if there are marked parameters
    # if '§' not in request_template:
    #     return jsonify({'error': 'No marked parameters found in the request template.'}), 400

    # Result container to store responses
    results = []
    logging.debug(f"Template sebelum menyimpan: {request_template}")
    for payload in payloads:
        # Replace the marked parameters with the current payload
        temp_request = replace_targets_with_payloads(request_template, payload)
        logging.debug(f"payload: {payloads}")
        logging.debug(f"Temp Requestnya: {temp_request}")
        # Parse the modified request to get method, path, host, headers, body, and protocol
        try:
            method, path, host, headers, body, protocol = parse_http_request(temp_request)
        except Exception as e:
            logging.error(f"Failed to parse request after replacing payload: {e}")
            continue
        
        # Prepare clean request before sending
        prepared_request = prepare_request_for_sending(temp_request)
        logging.debug(f"Template setelah modifikasi: {request_template}")
        # Construct URL for the request
        url = f"{'https' if protocol == 'HTTPS/1.1' else 'http'}://{host}{path}"

        try:
            # Send the request using the parsed method and details
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=body
            )

            # Store the result of the request
            result = {
                'payload': payload,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'response': response.text
            }

            # Log the results for debugging
            logging.debug(f"Request after replacing payload: {prepared_request}")
            logging.debug(f"Response: {response.status_code} - {response.text[:200]}")  # Log the first 200 chars
            results.append(result)

        except requests.RequestException as e:
            # If request fails, log the error and continue to the next payload
            logging.error(f"Failed to send request for payload {payload}: {e}")
            results.append({
                'payload': payload,
                'status_code': 'N/A',
                'response': str(e)
            })

    return jsonify({'results': results})

@app.route('/intruder/clear', methods=['POST'])
def clear_intruder():
    """Clear all request and response files in Intruder."""
    try:
        # Hapus semua file di folder requests
        for filename in os.listdir(INTRUDER_DIR):
            file_path = os.path.join(INTRUDER_DIR, filename)
            os.remove(file_path)

        logging.info("Intruder History cleared successfully.")
        return redirect(url_for('intruder'))
    except Exception as e:
        logging.error(f"Error clearing Intruder history: {e}")
        return jsonify({'error': 'Failed to clear Intruder history'}), 500

if __name__ == '__main__':
    socketio.run(app, debug=True)
