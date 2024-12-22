let currentResponseData = null;
    let currentFlowId = null;

    function showRequest(flow_id) {
        fetch(`/repeater/request/${flow_id}`)
            .then(response => response.json())
            .then(data => {
                const requestData = `${data.method} ${data.path} HTTP/1.1\nHost: ${data.host}\n${formatHeaders(data.headers)}\n\n${data.body}`;
                document.getElementById('requestData').value = requestData;
                currentFlowId = flow_id;
                document.getElementById('save-request').disabled = false;
            })
            .catch(error => {
                console.error('Error fetching request:', error);
            });
    }

    document.getElementById('send-request').addEventListener('click', function() {
        const requestData = document.getElementById('requestData').value;
        const parsedRequest = parseRequestData(requestData);

        fetch('/repeater/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(parsedRequest)
        })
        .then(response => {
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
                return response.json().then(data => {
                    currentResponseData = {
                        "raw": `${data.status}\n${formatHeaders(data.headers)}\n\n${data.body}`,
                        "html": data.body
                    };
                    showResponseAsRaw(); // Default view
                });
            } else {
                return response.text().then(text => {
                    currentResponseData = {
                        "raw": text,
                        "html": text
                    };
                    showResponseAsRaw(); // Default view
                });
            }
        })
        .catch(error => {
            console.error('Error sending request:', error);
            document.getElementById('response-body').textContent = 'Error: ' + error.message;
        });
    });

    document.getElementById('save-request').addEventListener('click', function() {
        const requestData = document.getElementById('requestData').value;
        const parsedRequest = parseRequestData(requestData);

        if (currentFlowId) {
            fetch(`/repeater/save/${currentFlowId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(parsedRequest)
            })
            .then(response => {
                if (response.ok) {
                    alert("Request saved successfully.");
                } else {
                    alert("Failed to save the request.");
                }
            })
            .catch(error => {
                console.error('Error saving request:', error);
                alert('Error: ' + error.message);
            });
        } else {
            alert("No request selected to save.");
        }
    });

    function parseRequestData(requestData) {
        const lines = requestData.split('\n');
        const [method, path] = lines[0].split(' ');
        const hostLine = lines.find(line => line.startsWith('Host:'));
        const host = hostLine ? hostLine.split(' ')[1] : '';
        const headerLines = lines.slice(1, lines.indexOf(''));
        const headers = {};

        headerLines.forEach(line => {
            const [key, ...value] = line.split(':');
            if (key && value) {
                headers[key.trim()] = value.join(':').trim();
            }
        });

        const body = lines.slice(lines.indexOf('') + 1).join('\n');

        return {
            method: method,
            host: host,
            path: path,
            headers: headers,
            body: body
        };
    }

    document.getElementById('view-json').addEventListener('click', showResponseAsRaw);
    document.getElementById('view-html').addEventListener('click', showResponseAsHTML);

    function showResponseAsRaw() {
        if (currentResponseData) {
            document.getElementById('response-body').innerHTML = `<pre>${escapeHTML(currentResponseData.raw)}</pre>`;
        }
    }

    function showResponseAsHTML() {
        if (currentResponseData) {
            const modal = document.getElementById("htmlResponseModal");
            const iframe = document.getElementById("responseIframe");

            const blob = new Blob([currentResponseData.html], { type: 'text/html' });
            iframe.src = URL.createObjectURL(blob);

            modal.style.display = "block";
        }
    }

    document.querySelector(".close").onclick = function () {
        document.getElementById("htmlResponseModal").style.display = "none";
    }

    window.onclick = function (event) {
        const modal = document.getElementById("htmlResponseModal");
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };

    function escapeHTML(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function formatHeaders(headers) {
        return Object.entries(headers).map(([key, value]) => `${key}: ${value}`).join('\n');
    }

    // Open documentation modal
    document.getElementById('btn-documentation').addEventListener('click', function() {
        document.getElementById('documentationModal').style.display = 'block';
    });

    // Close documentation modal
    document.querySelector('.close-documentation').addEventListener('click', function() {
        document.getElementById('documentationModal').style.display = 'none';
    });

    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('documentationModal');
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
