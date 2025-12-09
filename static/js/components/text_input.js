function showTextError(input, message) {
    const errorId = input.id + '-errors';
    let errorContainer = document.getElementById(errorId);

    if (!errorContainer) {
        const wrapper = input.closest('.text-input-container');
        if (wrapper) {
            errorContainer = wrapper.querySelector('.text-input-errors');
        }
    }

    if (!errorContainer) return;

    errorContainer.innerHTML = '';

    const p = document.createElement('p');
    p.className = 'text-input-error';

    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute('class', 'text-input-error-icon');
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

function clearTextError(input) {
    const errorId = input.id + '-errors';
    let errorContainer = document.getElementById(errorId);

    if (!errorContainer) {
        const wrapper = input.closest('.text-input-container');
        if (wrapper) {
            errorContainer = wrapper.querySelector('.text-input-errors');
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

    document.querySelectorAll('.text-input-field').forEach(input => {
        if (processedInputs.has(input)) return;
        processedInputs.add(input);

        // Validation logic
        const validate = () => {
            const minLength = input.getAttribute('minlength');
            const required = input.hasAttribute('required');
            const value = input.value;

            if (required && !value) {
                if (input.classList.contains('border-red-500')) {
                    showTextError(input, 'This field is required.');
                } else {
                    clearTextError(input);
                }
                return false;
            }

            if (value && minLength && value.length < parseInt(minLength)) {
                // Get label from input
                const label = input.closest('.text-input-container')?.querySelector('label')?.textContent.replace('*', '').trim() || 'Field';
                showTextError(input, `${label} must be at least ${minLength} characters long.`);
                return false;
            }

            clearTextError(input);
            return true;
        };

        input.addEventListener('blur', () => {
            if (input.required && !input.value) {
                showTextError(input, 'This field is required.');
            }
        });

        input.addEventListener('input', validate);

        // Attach submit listener only once per form
        const form = input.closest('form');
        if (form && !processedForms.has(form)) {
            processedForms.add(form);

            form.addEventListener('submit', e => {
                let hasError = false;

                form.querySelectorAll('.text-input-field').forEach(textInput => {
                    const minLength = textInput.getAttribute('minlength');
                    const label = textInput.closest('.text-input-container')?.querySelector('label')?.textContent.replace('*', '').trim() || 'This field';

                    if (textInput.required && !textInput.value) {
                        hasError = true;
                        showTextError(textInput, 'This field is required.');
                    } else if (textInput.value && minLength && textInput.value.length < parseInt(minLength)) {
                        hasError = true;
                        showTextError(textInput, `${label} must be at least ${minLength} characters long.`);
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
