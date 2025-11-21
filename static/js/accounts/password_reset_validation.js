document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('.auth-form-medium');
    const emailInput = document.getElementById('id_email');

    // Helper function to show error
    function showError(input, message) {
        const container = input.parentElement;
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
        const container = input.parentElement;
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

    function validateEmail(input) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(input.value.trim())) {
            showError(input, 'Please enter a valid email address.');
            return false;
        }
        clearError(input);
        return true;
    }

    // Real-time validation
    if (emailInput) {
        emailInput.addEventListener('input', () => {
            if (validateRequired(emailInput, 'Email')) {
                validateEmail(emailInput);
            }
        });
    }

    // Form submission validation
    if (form) {
        form.addEventListener('submit', function (event) {
            let isValid = true;

            if (emailInput) {
                if (!validateRequired(emailInput, 'Email')) {
                    isValid = false;
                } else if (!validateEmail(emailInput)) {
                    isValid = false;
                }
            }

            if (!isValid) {
                event.preventDefault();
            }
        });
    }
});
