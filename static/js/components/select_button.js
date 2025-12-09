document.addEventListener('DOMContentLoaded', () => {
    const selects = document.querySelectorAll('select.appearance-none');

    selects.forEach(select => {
        // Validation logic
        select.addEventListener('change', () => {
            validateSelect(select);
        });

        // Form submission validation
        const form = select.closest('form');
        if (form && !form.hasSelectButtonValidation) {
            form.hasSelectButtonValidation = true;
            form.addEventListener('submit', (e) => {
                let hasError = false;
                form.querySelectorAll('select.appearance-none').forEach(s => {
                    if (!validateSelect(s)) {
                        hasError = true;
                    }
                });

                if (hasError) {
                    e.preventDefault();
                    // Scroll to first invalid element
                    const firstInvalid = form.querySelector('.border-red-500');
                    if (firstInvalid) {
                        firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }
            });
        }
    });

    function validateSelect(select) {
        if (!select.required) return true;

        const container = select.parentElement.parentElement; // Adjust based on DOM structure
        const value = select.value;
        const isValid = value !== "";

        if (!isValid) {
            showError(select, container);
            return false;
        } else {
            clearError(select, container);
            return true;
        }
    }

    function showError(select, container) {
        // Add error styling
        select.classList.remove('border-slate-700', 'focus:border-slate-600', 'focus:ring-slate-500/30');
        select.classList.add('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/50');

        // Also style the arrow if possible (it's a sibling div)
        const arrowDiv = select.nextElementSibling;
        if (arrowDiv) {
            const svg = arrowDiv.querySelector('svg');
            if (svg) svg.style.color = '#ef4444';
        }

        // Add error message if not exists
        let errorDiv = container.querySelector('.select-button-errors');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'select-button-errors';
            errorDiv.style.cssText = "font-size: 0.875rem; color: #ef4444; margin-top: 0.25rem; display: flex; flex-direction: column; gap: 0.25rem;";
            container.appendChild(errorDiv);
        }

        if (!errorDiv.querySelector('.client-error')) {
            const errorP = document.createElement('p');
            errorP.className = 'client-error';
            errorP.style.cssText = "display: flex; align-items: center; gap: 0.25rem;";
            errorP.innerHTML = `
                <svg style="height: 1rem; width: 1rem;" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
                This field is required.
            `;
            errorDiv.appendChild(errorP);
        }
    }

    function clearError(select, container) {
        // Remove error styling
        select.classList.remove('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/50');
        select.classList.add('border-slate-700', 'focus:border-slate-600', 'focus:ring-slate-500/30');

        // Reset arrow style (relies on CSS for hover/focus only, forcing color might stick)
        const arrowDiv = select.nextElementSibling;
        if (arrowDiv) {
            const svg = arrowDiv.querySelector('svg');
            if (svg) svg.style.color = ''; // Reset to inherit/default
        }

        // Remove error message
        const errorDiv = container.querySelector('.select-button-errors');
        if (errorDiv) {
            const clientError = errorDiv.querySelector('.client-error');
            if (clientError) clientError.remove();
            if (errorDiv.children.length === 0) errorDiv.remove();
        }
    }
});
