$(document).ready(function() {
    // Configure button click event
    $(document).on('click', '.configure-btn', function(e) {
        e.preventDefault();
        const flowId = $(this).data('flow-id');

        // Reset modal content before showing it again
        $('#config-container').empty();

        // Show the modal
        var modal = new bootstrap.Modal(document.getElementById('configModal'));
        modal.show();

        // Use AJAX to fetch the configuration page
        $.ajax({
            url: `/intruder/configure/${flowId}`,
            type: 'GET',
            success: function(data) {
                // Inject the fetched content into the modal's container
                $('#config-container').html(data);
            },
            error: function(xhr, status, error) {
                console.error('Error fetching configuration:', error);
            }
        });
    });

    // Ensure modal opens when clicking configure button again
    $('#configModal').on('show.bs.modal', function () {
        // Optionally, log or debug if needed
        console.log('Modal is about to be shown');
    });

    $(document).on('click', '.configure-btn', function() {
        $('#configModal').modal('show');
    });

    // Reset modal content when hidden
    $('#configModal').on('hidden.bs.modal', function () {
        $('#config-container').empty(); // Clear the modal content
    });

    // Handle "Clear All" button click
    $('#clear-all').on('click', function(e) {
        e.preventDefault();
        fetch('/intruder/clear', { method: 'POST' })
            .then(response => {
                if (response.ok) {
                    location.reload(); // Reload page on successful clear
                } else {
                    alert('Failed to clear history.');
                }
            })
            .catch(error => {
                console.error('Error clearing history:', error);
            });
    });
});