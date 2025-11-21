document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('.auth-form-large');
    const firstNameInput = document.getElementById('id_first_name');
    const lastNameInput = document.getElementById('id_last_name');
    const emailInput = document.getElementById('id_email');
    const usernameInput = document.getElementById('id_username');
    const password1Input = document.getElementById('id_password1');
    const password2Input = document.getElementById('id_password2');
    const submitButton = form.querySelector('button[type="submit"]');

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
    firstNameInput.addEventListener('input', () => validateRequired(firstNameInput, 'First Name'));
    lastNameInput.addEventListener('input', () => validateRequired(lastNameInput, 'Last Name'));
    usernameInput.addEventListener('input', () => validateRequired(usernameInput, 'Username'));
    emailInput.addEventListener('input', () => {
        if (validateRequired(emailInput, 'Email')) {
            validateEmail(emailInput);
        }
    });
    password1Input.addEventListener('input', () => {
        if (validateRequired(password1Input, 'Password')) {
            validatePasswordStrength(password1Input);
        }
        if (password2Input.value) validatePasswordMatch();
    });
    password2Input.addEventListener('input', () => {
        if (validateRequired(password2Input, 'Confirm Password')) {
            validatePasswordMatch();
        }
    });

    // Form submission validation
    form.addEventListener('submit', function (event) {
        let isValid = true;

        if (!validateRequired(firstNameInput, 'First Name')) isValid = false;
        if (!validateRequired(lastNameInput, 'Last Name')) isValid = false;
        if (!validateRequired(usernameInput, 'Username')) isValid = false;

        if (!validateRequired(emailInput, 'Email')) {
            isValid = false;
        } else if (!validateEmail(emailInput)) {
            isValid = false;
        }

        if (!validateRequired(password1Input, 'Password')) {
            isValid = false;
        } else if (!validatePasswordStrength(password1Input)) {
            isValid = false;
        }

        if (!validateRequired(password2Input, 'Confirm Password')) {
            isValid = false;
        } else if (!validatePasswordMatch()) {
            isValid = false;
        }

        if (!isValid) {
            event.preventDefault();
        }
    });
});
