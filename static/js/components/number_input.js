function showNumberError(input, message) {
    const errorId = input.id + '-errors';
    let errorContainer = document.getElementById(errorId);

    if (!errorContainer) {
        const wrapper = input.closest('.number-input-container');
        if (wrapper) {
            errorContainer = wrapper.querySelector('.number-input-errors');
        }
    }

    if (!errorContainer) return;

    errorContainer.innerHTML = '';

    const p = document.createElement('p');
    p.className = 'number-input-error';

    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute('class', 'number-input-error-icon');
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

function clearNumberError(input) {
    const errorId = input.id + '-errors';
    let errorContainer = document.getElementById(errorId);

    if (!errorContainer) {
        const wrapper = input.closest('.number-input-container');
        if (wrapper) {
            errorContainer = wrapper.querySelector('.number-input-errors');
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

    document.querySelectorAll('.number-input-field').forEach(input => {
        if (processedInputs.has(input)) return;
        processedInputs.add(input);

        // Validation logic
        const validate = () => {
            const min = input.getAttribute('min');
            const max = input.getAttribute('max');
            const required = input.hasAttribute('required');
            const value = parseFloat(input.value);
            const hasValue = input.value.trim() !== '';

            if (required && !hasValue) {
                if (input.classList.contains('border-red-500')) {
                    showNumberError(input, 'This field is required.');
                } else {
                    clearNumberError(input);
                }
                return false;
            }

            if (hasValue) {
                if (min && value < parseFloat(min)) {
                    const label = input.closest('.number-input-container')?.querySelector('label')?.textContent.replace('*', '').trim() || 'Value';
                    showNumberError(input, `${label} must be at least ${min}.`);
                    return false;
                }
                if (max && value > parseFloat(max)) {
                    const label = input.closest('.number-input-container')?.querySelector('label')?.textContent.replace('*', '').trim() || 'Value';
                    showNumberError(input, `${label} must be at most ${max}.`);
                    return false;
                }
            }

            clearNumberError(input);
            return true;
        };

        input.addEventListener('blur', () => {
            if (input.required && !input.value.trim()) {
                showNumberError(input, 'This field is required.');
            }
        });

        input.addEventListener('input', validate);

        // Attach submit listener only once per form
        const form = input.closest('form');
        if (form && !processedForms.has(form)) {
            processedForms.add(form);

            form.addEventListener('submit', e => {
                let hasError = false;

                form.querySelectorAll('.number-input-field').forEach(numInput => {
                    const min = numInput.getAttribute('min');
                    const max = numInput.getAttribute('max');
                    const value = parseFloat(numInput.value);
                    const hasValue = numInput.value.trim() !== '';
                    const label = numInput.closest('.number-input-container')?.querySelector('label')?.textContent.replace('*', '').trim() || 'This field';

                    if (numInput.required && !hasValue) {
                        hasError = true;
                        showNumberError(numInput, 'This field is required.');
                    } else if (hasValue) {
                        if (min && value < parseFloat(min)) {
                            hasError = true;
                            showNumberError(numInput, `${label} must be at least ${min}.`);
                        } else if (max && value > parseFloat(max)) {
                            hasError = true;
                            showNumberError(numInput, `${label} must be at most ${max}.`);
                        }
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
