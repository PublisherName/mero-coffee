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
    const errorId = input.id + '-errors';
    let errorContainer = document.getElementById(errorId);

    if (!errorContainer) {
        const wrapper = input.closest('.password-input-container');
        if (wrapper) {
            errorContainer = wrapper.querySelector('.password-input-errors');
        }
    }

    if (!errorContainer) return;

    errorContainer.innerHTML = '';

    const p = document.createElement('p');
    p.className = 'password-input-error';

    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute('class', 'password-input-error-icon');
    svg.setAttribute('fill', 'currentColor');
    svg.setAttribute('viewBox', '0 0 20 20');

    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute('fill-rule', 'evenodd');
    path.setAttribute('d', 'M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z');
    path.setAttribute('clip-rule', 'evenodd');

    svg.appendChild(path);
    p.appendChild(svg);

    p.appendChild(document.createTextNode(' ' + message));

    errorContainer.appendChild(p);

    input.classList.remove('border-slate-700', 'focus:border-slate-600', 'focus:ring-slate-500/30');
    input.classList.add('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/50');
}

function clearError(input) {
    const errorId = input.id + '-errors';
    let errorContainer = document.getElementById(errorId);

    if (!errorContainer) {
        const wrapper = input.closest('.password-input-container');
        if (wrapper) {
            errorContainer = wrapper.querySelector('.password-input-errors');
        }
    }

    if (errorContainer) {
        errorContainer.innerHTML = '';
    }

    input.classList.remove('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/50');
    input.classList.add('border-slate-700', 'focus:border-slate-600', 'focus:ring-slate-500/30');
}

document.addEventListener('DOMContentLoaded', () => {
    const processedForms = new Set();
    const processedInputs = new Set();

    document.querySelectorAll('input[type="password"]').forEach(input => {
        if (processedInputs.has(input)) return;
        processedInputs.add(input);

        const validate = () => {
            const minLength = input.getAttribute('minlength');
            const required = input.hasAttribute('required');
            const value = input.value;

            if (required && !value) {
                if (input.classList.contains('border-red-500')) {
                    showError(input, 'This field is required.');
                } else {
                    clearError(input);
                }
                return false;
            }

            if (value && minLength && value.length < parseInt(minLength)) {
                showError(input, `Password must be at least ${minLength} characters long.`);
                return false;
            }

            clearError(input);
            return true;
        };

        input.addEventListener('blur', () => {
            if (input.required && !input.value) {
                showError(input, 'This field is required.');
            }
        });

        input.addEventListener('input', validate);

        const form = input.closest('form');
        if (form && !processedForms.has(form)) {
            processedForms.add(form);

            form.addEventListener('submit', e => {
                let hasError = false;

                form.querySelectorAll('input[type="password"]').forEach(pwdInput => {
                    const minLength = pwdInput.getAttribute('minlength');

                    if (pwdInput.required && !pwdInput.value) {
                        hasError = true;
                        showError(pwdInput, 'This field is required.');
                    } else if (pwdInput.value && minLength && pwdInput.value.length < parseInt(minLength)) {
                        hasError = true;
                        showError(pwdInput, `Password must be at least ${minLength} characters long.`);
                    }
                });

                if (hasError) {
                    e.preventDefault();
                    const firstError = form.querySelector('.border-red-500');
                    if (firstError) firstError.focus();
                }
            });
        }
    });
});
