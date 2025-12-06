function togglePassword(fieldId) {
    const input = document.getElementById(fieldId);
    const eyeOpen = document.getElementById(fieldId + '-eye-open');
    const eyeClosed = document.getElementById(fieldId + '-eye-closed');

    if (input.type === 'password') {
        input.type = 'text';
        eyeOpen.style.display = 'none';
        eyeClosed.style.display = 'block';
    } else {
        input.type = 'password';
        eyeOpen.style.display = 'block';
        eyeClosed.style.display = 'none';
    }
}

function showError(input, message) {
    const container = input.closest('.password-input-wrapper') || input.closest('.input-container');
    if (!container) return;

    let error = container.querySelector('.client-error');
    if (!error) {
        error = document.createElement('p');
        error.className = 'auth-error client-error';
        container.appendChild(error);
    }
    error.textContent = message;
    input.classList.remove('border-slate-700', 'focus:border-slate-600', 'focus:ring-slate-500/30');
    input.classList.add('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/50');
}

function clearError(input) {
    const container = input.closest('.password-input-wrapper') || input.closest('.input-container');
    if (!container) return;

    const error = container.querySelector('.client-error');
    if (error) error.remove();

    input.classList.remove('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/50');
    input.classList.add('border-slate-700', 'focus:border-slate-600', 'focus:ring-slate-500/30');
}

document.addEventListener('DOMContentLoaded', () => {
    const processedForms = new Set();

    document.querySelectorAll('input[type="password"]').forEach(input => {
        // Initial styling if there is an error message already present
        const wrapper = input.closest('.password-input-wrapper');
        if (wrapper && wrapper.querySelector('.password-input-error, .auth-error, .client-error')) {
            showError(input, wrapper.querySelector('.client-error, .auth-error').textContent);
        }

        // Clear error on input when there's value, show error if required and empty
        input.addEventListener('input', () => {
            if (input.value.trim()) {
                clearError(input);
            } else if (input.required) {
                showError(input, 'Password is required.');
            }
        });

        // Attach submit listener only once per form
        const form = input.closest('form');
        if (form && !processedForms.has(form)) {
            processedForms.add(form);

            form.addEventListener('submit', e => {
                let hasError = false;

                form.querySelectorAll('input[type="password"]').forEach(pwdInput => {
                    if (pwdInput.required && !pwdInput.value.trim()) {
                        hasError = true;
                        showError(pwdInput, 'Password is required.');
                    }
                });

                if (hasError) e.preventDefault();
            });
        }
    });
});
