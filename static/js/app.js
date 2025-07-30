// ModularNucleoid P2P Demo JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log("ModularNucleoid P2P Demo loaded successfully");

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Add loading states to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Loading...';
            }
        });
    });
});

// Utility functions
function showToast(message, type = 'info') {
    // Create a simple toast notification
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        // Create container if it doesn't exist
        const newToastContainer = document.createElement('div');
        newToastContainer.className = 'toast-container';
        document.body.appendChild(newToastContainer);
        toastContainer = newToastContainer;
    }

    const toastElement = document.createElement('div');
    toastElement.className = `alert alert-${type} alert-dismissible fade show`;
    toastElement.setAttribute('role', 'alert');
    toastElement.innerHTML = `
        <div>${message}</div>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    toastContainer.appendChild(toastElement);

    // Auto-hide after 3 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(toastElement);
        bsAlert.close();
    }, 3000);
}
