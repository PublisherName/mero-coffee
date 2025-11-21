document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('.auth-form-medium');
    const password1Input = document.getElementById('new_password1');
    const password2Input = document.getElementById('new_password2');

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

    function validatePasswordMatch() {
        if (password1Input.value !== password2Input.value) {
            showError(password2Input, 'Passwords do not match.');
            return false;
        }
        clearError(password2Input);
        return true;
    }

    function validatePasswordStrength(input) {
        if (input.value.length < 8) {
            showError(input, 'Password must be at least 8 characters long.');
            return false;
        }
        clearError(input);
        return true;
    }

    // Real-time validation
    if (password1Input) {
        password1Input.addEventListener('input', () => {
            if (validateRequired(password1Input, 'New Password')) {
                validatePasswordStrength(password1Input);
            }
            if (password2Input.value) validatePasswordMatch();
        });
    }
    if (password2Input) {
        password2Input.addEventListener('input', () => {
            if (validateRequired(password2Input, 'Confirm New Password')) {
                validatePasswordMatch();
            }
        });
    }

    // Form submission validation
    if (form) {
        form.addEventListener('submit', function (event) {
            let isValid = true;

            if (password1Input) {
                if (!validateRequired(password1Input, 'New Password')) {
                    isValid = false;
                } else if (!validatePasswordStrength(password1Input)) {
                    isValid = false;
                }
            }

            if (password2Input) {
                if (!validateRequired(password2Input, 'Confirm New Password')) {
                    isValid = false;
                } else if (!validatePasswordMatch()) {
                    isValid = false;
                }
            }

            if (!isValid) {
                event.preventDefault();
            }
        });
    }
});
