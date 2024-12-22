const socket = io.connect('http://' + document.domain + ':' + location.port);


    // Fungsi untuk mengambil data HTTP history
    function fetchHttpHistory() {
        socket.emit('get_http_history'); // Emit request untuk mendapatkan data history terbaru
    }
    function showDetails(flow_id) {
        fetch(`/http-history/details/${flow_id}`)
        .then(response => response.json())
        .then(data => {
            const requestBody = data.request.trim();
            const responseBody = data.response.trim();
            document.getElementById('request-body').textContent = requestBody;
            document.getElementById('response-body').textContent = responseBody;
        })
        .catch(error => {
            console.error('Error fetching details:', error);
            document.getElementById('request-body').textContent = 'Error fetching request details';
            document.getElementById('response-body').textContent = 'Error fetching response details';
        });
    }

    // Clear all HTTP history
    document.getElementById('clear-all-form').addEventListener('submit', function(event) {
        event.preventDefault();
        fetch('/http-history/clear', { method: 'POST' })
        .then(response => {
            if (response.ok) {
                location.reload(); // Reload halaman jika berhasil
            } else {
                alert('Failed to clear history.');
            }
        })
        .catch(error => {
            console.error('Error clearing history:', error);
        });
    });

    // Muat data saat halaman dibuka
    document.addEventListener('DOMContentLoaded', function () {
        fetchHttpHistory();
    });

    let lastSelectedFlowId = null; // Variabel untuk menyimpan flow_id terakhir yang diklik
    // Mendengarkan data history dari server
    socket.on('http_history_data', function(data) {
        const tableBody = document.getElementById('http-history-table-body');
        tableBody.innerHTML = ''; // Bersihkan tabel

        // Tambahkan data baru ke tabel
        data.forEach((request, index) => {
            const row = document.createElement('tr');
            row.style.cursor = 'pointer';
            row.addEventListener('click', () => {
                showDetails(request.flow_id);
                highlightRow(row); // Highlight baris yang dipilih
                lastSelectedFlowId = request.flow_id; // Simpan flow_id yang terakhir dipilih
            });

            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${request.method}</td>
                <td>${request.host}</td>
                <td>${request.url}</td>
                <td>${request.status}</td>
                <td>
                    <a href="/send-to-repeater/${request.flow_id}" class="btn btn-sm btn-repeater">Send to Repeater</a>
                    <a href="/send-to-intruder/${request.flow_id}" class="btn btn-sm btn-intruder">Send to Intruder</a>
                </td>
            `;
            tableBody.appendChild(row);
            if (!request.flow_id) {
            console.error(`Request missing flow_id:`, request);
            }

            // Jika flow_id cocok dengan yang terakhir dipilih, tambahkan highlight
            if (request.flow_id === lastSelectedFlowId) {
                highlightRow(row);
            }
        });
    });

    function highlightRow(row) {
        // Hapus highlight dari semua baris
        document.querySelectorAll('#http-history-table tbody tr').forEach(tr => {
            tr.classList.remove('highlighted');
        });
        // Tambahkan highlight ke baris yang dipilih
        row.classList.add('highlighted');
    }

    // Refresh tabel setiap 5 detik
    setInterval(fetchHttpHistory, 5000);