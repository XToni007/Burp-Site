function insertSymbol() {
    let requestBox = document.getElementById('request');
    let startPos = requestBox.selectionStart;
    let endPos = requestBox.selectionEnd;
    let text = requestBox.value;
    
    // Gunakan simbol yang lebih netral untuk menandai
    let symbolText = '§' + text.substring(startPos, endPos) + '§';
    
    // Simpan perubahan ke dalam textarea
    requestBox.value = text.substring(0, startPos) + symbolText + text.substring(endPos);
}

$('#configure-intruder-form').on('submit', function(e) {
    e.preventDefault(); // Prevent actual form submission
    
    let formData = new FormData(this);
    formData.append('request_content', $('#request').val());

    $.ajax({
        type: 'POST',
        url: this.action,
        processData: false,
        contentType: false,
        data: formData,
        success: function(response) {
            alert('Configuration saved successfully!');
        },
        error: function(error) {
            alert('Failed to save configuration.');
        }
    });
});

$(document).ready(function() {
    $('#start-attack').on('click', function() {
        let flowId = $('input[name="flow_id"]').val();
        if (!flowId) {
            alert('Flow ID is missing.');
            return;
        }

        $.ajax({
            type: 'POST',
            url: '/intruder/run',
            contentType: 'application/json',
            data: JSON.stringify({ flow_id: flowId }),
            success: function(response) {
                processResults(response.results);
            },
            error: function(error) {
                alert('An error occurred: ' + escapeHtml(error.responseJSON.error));
            }
        });
    });

    function processResults(results) {
        let resultsTableBody = $('#results-table-body');
        resultsTableBody.empty();

        results.forEach(function(result) {
            let headersString = result.headers ? JSON.stringify(result.headers, null, 2) : 'Tidak ada header yang dikembalikan';
            let bodyString = result.response ? result.response : 'Tidak ada isi respons';

            if (!result.response_headers) {
                console.warn('Response headers undefined for payload:', result.payload);
            }
            if (!result.response_body) {
                console.warn('Response body undefined for payload:', result.payload);
            }

            let row = `<tr>
                <td>${escapeHtml(result.payload)}</td>
                <td>${escapeHtml(result.status_code.toString())}</td>
                <td><div class="scrollable-cell">${escapeHtml(headersString)}</div></td>
                <td><div class="scrollable-cell">${escapeHtml(bodyString)}</div></td>
            </tr>`;
            resultsTableBody.append(row);
        });
    }
});

function escapeHtml(unsafe) {
    if (typeof unsafe !== 'string') {
        unsafe = String(unsafe); 
    }
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}