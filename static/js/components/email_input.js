function showEmailError(input, message) {
    const errorId = input.id + '-errors';
    let errorContainer = document.getElementById(errorId);

    if (!errorContainer) {
        const wrapper = input.closest('.email-input-container');
        if (wrapper) {
            errorContainer = wrapper.querySelector('.email-input-errors');
        }
    }

    if (!errorContainer) return;

    errorContainer.innerHTML = '';

    const p = document.createElement('p');
    p.className = 'email-input-error';

    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute('class', 'email-input-error-icon');
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

function clearEmailError(input) {
    const errorId = input.id + '-errors';
    let errorContainer = document.getElementById(errorId);

    if (!errorContainer) {
        const wrapper = input.closest('.email-input-container');
        if (wrapper) {
            errorContainer = wrapper.querySelector('.email-input-errors');
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
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    document.querySelectorAll('.email-input-field').forEach(input => {
        if (processedInputs.has(input)) return;
        processedInputs.add(input);

        // Validation logic
        const validate = () => {
            const required = input.hasAttribute('required');
            const value = input.value.trim();

            if (required && !value) {
                if (input.classList.contains('border-red-500')) {
                    showEmailError(input, 'This field is required.');
                } else {
                    clearEmailError(input);
                }
                return false;
            }

            if (value && !emailPattern.test(value)) {
                showEmailError(input, 'Please enter a valid email address.');
                return false;
            }

            clearEmailError(input);
            return true;
        };

        input.addEventListener('blur', () => {
            if (input.required && !input.value.trim()) {
                showEmailError(input, 'This field is required.');
            }
        });

        input.addEventListener('input', validate);

        // Attach submit listener only once per form
        const form = input.closest('form');
        if (form && !processedForms.has(form)) {
            processedForms.add(form);

            form.addEventListener('submit', e => {
                let hasError = false;

                form.querySelectorAll('.email-input-field').forEach(emailInput => {
                    const value = emailInput.value.trim();
                    if (emailInput.required && !value) {
                        hasError = true;
                        showEmailError(emailInput, 'This field is required.');
                    } else if (value && !emailPattern.test(value)) {
                        hasError = true;
                        showEmailError(emailInput, 'Please enter a valid email address.');
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
