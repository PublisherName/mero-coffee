document.addEventListener('DOMContentLoaded', () => {
    const forms = new Set();
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    document.querySelectorAll('.email-input-field').forEach(input => {
        const container = input.closest('.email-input-container');
        if (container && container.querySelector('.email-input-error, .auth-error, .client-error')) {
            input.classList.remove('border-slate-700', 'focus:border-slate-600', 'focus:ring-slate-500/30');
            input.classList.add('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/50');
        }
        
        input.addEventListener('input', () => {
            const container = input.closest('.email-input-container');
            if (!container) return;
            
            const error = container.querySelector('.client-error');
            
            if (!input.value.trim() && input.required) {
                if (!error) {
                    const newError = document.createElement('p');
                    newError.className = 'auth-error client-error';
                    newError.textContent = 'Email is required.';
                    container.appendChild(newError);
                }
                input.classList.remove('border-slate-700', 'focus:border-slate-600', 'focus:ring-slate-500/30');
                input.classList.add('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/50');
            } else if (input.value.trim() && !emailPattern.test(input.value)) {
                if (!error) {
                    const newError = document.createElement('p');
                    newError.className = 'auth-error client-error';
                    newError.textContent = 'Please enter a valid email address.';
                    container.appendChild(newError);
                } else {
                    error.textContent = 'Please enter a valid email address.';
                }
                input.classList.remove('border-slate-700', 'focus:border-slate-600', 'focus:ring-slate-500/30');
                input.classList.add('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/50');
            } else if (input.value.trim()) {
                if (error) error.remove();
                input.classList.remove('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/50');
                input.classList.add('border-slate-700', 'focus:border-slate-600', 'focus:ring-slate-500/30');
            }
        });
        
        const form = input.closest('form');
        if (form && !forms.has(form)) {
            forms.add(form);
            form.addEventListener('submit', (e) => {
                let hasError = false;
                form.querySelectorAll('.email-input-field').forEach(emailInput => {
                    const container = emailInput.closest('.email-input-container');
                    
                    if (emailInput.required && !emailInput.value.trim()) {
                        hasError = true;
                        if (container) {
                            let error = container.querySelector('.client-error');
                            if (!error) {
                                error = document.createElement('p');
                                error.className = 'auth-error client-error';
                                container.appendChild(error);
                            }
                            error.textContent = 'Email is required.';
                            emailInput.classList.remove('border-slate-700', 'focus:border-slate-600', 'focus:ring-slate-500/30');
                            emailInput.classList.add('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/50');
                        }
                    } else if (emailInput.value.trim() && !emailPattern.test(emailInput.value)) {
                        hasError = true;
                        if (container) {
                            let error = container.querySelector('.client-error');
                            if (!error) {
                                error = document.createElement('p');
                                error.className = 'auth-error client-error';
                                container.appendChild(error);
                            }
                            error.textContent = 'Please enter a valid email address.';
                            emailInput.classList.remove('border-slate-700', 'focus:border-slate-600', 'focus:ring-slate-500/30');
                            emailInput.classList.add('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/50');
                        }
                    }
                });
                if (hasError) e.preventDefault();
            });
        }
    });
});
