function showTextareaError(textarea, message) {
    const errorId = textarea.id + '-errors';
    let errorContainer = document.getElementById(errorId);

    if (!errorContainer) {
        const wrapper = textarea.closest('.textarea-input-container');
        if (wrapper) {
            errorContainer = wrapper.querySelector('.textarea-input-errors');
        }
    }

    if (!errorContainer) return;

    errorContainer.innerHTML = '';

    const p = document.createElement('p');
    p.className = 'textarea-input-error';

    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute('class', 'textarea-input-error-icon');
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

    textarea.classList.remove('border-slate-700', 'focus:border-slate-600', 'focus:ring-slate-500/30');
    textarea.classList.add('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/50');
}

function clearTextareaError(textarea) {
    const errorId = textarea.id + '-errors';
    let errorContainer = document.getElementById(errorId);

    if (!errorContainer) {
        const wrapper = textarea.closest('.textarea-input-container');
        if (wrapper) {
            errorContainer = wrapper.querySelector('.textarea-input-errors');
        }
    }

    if (errorContainer) {
        errorContainer.innerHTML = '';
    }

    textarea.classList.remove('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/50');
    textarea.classList.add('border-slate-700', 'focus:border-slate-600', 'focus:ring-slate-500/30');
}

document.addEventListener('DOMContentLoaded', () => {
    const processedForms = new Set();
    const processedInputs = new Set();

    document.querySelectorAll('.textarea-input-field').forEach(textarea => {
        if (processedInputs.has(textarea)) return;
        processedInputs.add(textarea);

        // Validation logic
        const validate = () => {
            const minLength = textarea.getAttribute('minlength');
            const required = textarea.hasAttribute('required');
            const value = textarea.value.trim();

            if (required && !value) {
                if (textarea.classList.contains('border-red-500')) {
                    showTextareaError(textarea, 'This field is required.');
                } else {
                    clearTextareaError(textarea);
                }
                return false;
            }

            if (value && minLength && value.length < parseInt(minLength)) {
                const label = textarea.closest('.textarea-input-container')?.querySelector('label')?.textContent.replace('*', '').trim() || 'Field';
                showTextareaError(textarea, `${label} must be at least ${minLength} characters long.`);
                return false;
            }

            clearTextareaError(textarea);
            return true;
        };

        textarea.addEventListener('blur', () => {
            if (textarea.required && !textarea.value.trim()) {
                showTextareaError(textarea, 'This field is required.');
            }
        });

        textarea.addEventListener('input', validate);

        // Attach submit listener only once per form
        const form = textarea.closest('form');
        if (form && !processedForms.has(form)) {
            processedForms.add(form);

            form.addEventListener('submit', e => {
                let hasError = false;

                form.querySelectorAll('.textarea-input-field').forEach(textareaInput => {
                    const minLength = textareaInput.getAttribute('minlength');
                    const value = textareaInput.value.trim();
                    const label = textareaInput.closest('.textarea-input-container')?.querySelector('label')?.textContent.replace('*', '').trim() || 'This field';

                    if (textareaInput.required && !value) {
                        hasError = true;
                        showTextareaError(textareaInput, 'This field is required.');
                    } else if (value && minLength && value.length < parseInt(minLength)) {
                        hasError = true;
                        showTextareaError(textareaInput, `${label} must be at least ${minLength} characters long.`);
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
