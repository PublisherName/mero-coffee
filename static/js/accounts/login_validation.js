document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('.auth-form');
    const usernameInput = document.getElementById('id_username');
    const passwordInput = document.getElementById('id_password');

    // Helper function to show error
    function showError(input, message) {
        let container = input.parentElement;
        if (container.classList.contains('password-field-wrapper')) {
            container = container.parentElement;
        }

        let error = container.querySelector('.client-error');
        if (!error) {
            error = document.createElement('p');
            error.className = 'auth-error client-error';
            container.appendChild(error);
        }
        error.textContent = message;
        error.style.display = 'block';

        input.classList.add('border-red-500');
    }

    // Helper function to clear error
    function clearError(input) {
        let container = input.parentElement;
        if (container.classList.contains('password-field-wrapper')) {
            container = container.parentElement;
        }

        const error = container.querySelector('.client-error');
        if (error) {
            error.style.display = 'none';
        }
        input.classList.remove('border-red-500');
    }

    // Validation functions
    function validateRequired(input, fieldName) {
        if (!input.value.trim()) {
            showError(input, `${fieldName} is required.`);
            return false;
        }
        clearError(input);
        return true;
    }

    // Real-time validation
    if (usernameInput) {
        usernameInput.addEventListener('input', () => validateRequired(usernameInput, 'Username'));
    }
    if (passwordInput) {
        passwordInput.addEventListener('input', () => validateRequired(passwordInput, 'Password'));
    }

    // Form submission validation
    if (form) {
        form.addEventListener('submit', function (event) {
            let isValid = true;

            if (usernameInput && !validateRequired(usernameInput, 'Username')) isValid = false;
            if (passwordInput && !validateRequired(passwordInput, 'Password')) isValid = false;

            if (!isValid) {
                event.preventDefault();
            }
        });
    }
});
