document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('.auth-form');
    const usernameInput = document.getElementById('id_username');

    function showError(input, message) {
        const container = input.closest('.input-container');
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
        const container = input.closest('.input-container');
        if (!container) return;
        
        const error = container.querySelector('.client-error');
        if (error) error.remove();
        
        input.classList.remove('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/50');
        input.classList.add('border-slate-700', 'focus:border-slate-600', 'focus:ring-slate-500/30');
    }

    function validateRequired(input, fieldName) {
        if (!input.value.trim()) {
            showError(input, `${fieldName} is required.`);
            return false;
        }
        clearError(input);
        return true;
    }

    if (usernameInput) {
        usernameInput.addEventListener('input', () => {
            if (usernameInput.value.trim()) {
                clearError(usernameInput);
            }
        });
    }

    if (form) {
        form.addEventListener('submit', function (event) {
            let isValid = true;
            if (usernameInput && !validateRequired(usernameInput, 'Username')) isValid = false;
            if (!isValid) event.preventDefault();
        });
    }
});
