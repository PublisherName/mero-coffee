document.addEventListener('DOMContentLoaded', () => {
    const forms = new Set();
    
    document.querySelectorAll('.text-input-field').forEach(input => {
        const container = input.closest('.text-input-container');
        if (container && container.querySelector('.text-input-error, .auth-error, .client-error')) {
            input.classList.remove('border-slate-700', 'focus:border-slate-600', 'focus:ring-slate-500/30');
            input.classList.add('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/50');
        }
        
        input.addEventListener('input', () => {
            const container = input.closest('.text-input-container');
            if (!container) return;
            
            const error = container.querySelector('.client-error');
            
            if (input.value.trim()) {
                if (error) error.remove();
                input.classList.remove('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/50');
                input.classList.add('border-slate-700', 'focus:border-slate-600', 'focus:ring-slate-500/30');
            } else if (input.required) {
                if (!error) {
                    const newError = document.createElement('p');
                    newError.className = 'auth-error client-error';
                    newError.textContent = `${input.labels[0]?.textContent.replace('*', '').trim() || 'This field'} is required.`;
                    container.appendChild(newError);
                }
                input.classList.remove('border-slate-700', 'focus:border-slate-600', 'focus:ring-slate-500/30');
                input.classList.add('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/50');
            }
        });
        
        const form = input.closest('form');
        if (form && !forms.has(form)) {
            forms.add(form);
            form.addEventListener('submit', (e) => {
                let hasError = false;
                form.querySelectorAll('.text-input-field').forEach(textInput => {
                    if (textInput.required && !textInput.value.trim()) {
                        hasError = true;
                        const container = textInput.closest('.text-input-container');
                        if (container) {
                            let error = container.querySelector('.client-error');
                            if (!error) {
                                error = document.createElement('p');
                                error.className = 'auth-error client-error';
                                container.appendChild(error);
                            }
                            error.textContent = `${textInput.labels[0]?.textContent.replace('*', '').trim() || 'This field'} is required.`;
                            textInput.classList.remove('border-slate-700', 'focus:border-slate-600', 'focus:ring-slate-500/30');
                            textInput.classList.add('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/50');
                        }
                    }
                });
                if (hasError) e.preventDefault();
            });
        }
    });
});
