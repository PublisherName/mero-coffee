document.addEventListener('DOMContentLoaded', () => {
    const forms = new Set();
    
    document.querySelectorAll('.textarea-input-field').forEach(textarea => {
        const container = textarea.closest('.textarea-input-container');
        if (container && container.querySelector('.textarea-input-error, .auth-error, .client-error')) {
            textarea.classList.remove('border-slate-700', 'focus:border-slate-600', 'focus:ring-slate-500/30');
            textarea.classList.add('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/50');
        }
        
        textarea.addEventListener('input', () => {
            const container = textarea.closest('.textarea-input-container');
            if (!container) return;
            
            const error = container.querySelector('.client-error');
            
            if (!textarea.value.trim() && textarea.required) {
                if (!error) {
                    const newError = document.createElement('p');
                    newError.className = 'auth-error client-error';
                    newError.textContent = `${textarea.labels[0]?.textContent.replace('*', '').trim() || 'This field'} is required.`;
                    container.appendChild(newError);
                }
                textarea.classList.remove('border-slate-700', 'focus:border-slate-600', 'focus:ring-slate-500/30');
                textarea.classList.add('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/50');
            } else if (textarea.value.trim()) {
                if (error) error.remove();
                textarea.classList.remove('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/50');
                textarea.classList.add('border-slate-700', 'focus:border-slate-600', 'focus:ring-slate-500/30');
            }
        });
        
        const form = textarea.closest('form');
        if (form && !forms.has(form)) {
            forms.add(form);
            form.addEventListener('submit', (e) => {
                let hasError = false;
                form.querySelectorAll('.textarea-input-field').forEach(textareaInput => {
                    if (textareaInput.required && !textareaInput.value.trim()) {
                        hasError = true;
                        const container = textareaInput.closest('.textarea-input-container');
                        if (container) {
                            let error = container.querySelector('.client-error');
                            if (!error) {
                                error = document.createElement('p');
                                error.className = 'auth-error client-error';
                                container.appendChild(error);
                            }
                            error.textContent = `${textareaInput.labels[0]?.textContent.replace('*', '').trim() || 'This field'} is required.`;
                            textareaInput.classList.remove('border-slate-700', 'focus:border-slate-600', 'focus:ring-slate-500/30');
                            textareaInput.classList.add('border-red-500', 'focus:border-red-500', 'focus:ring-red-500/50');
                        }
                    }
                });
                if (hasError) e.preventDefault();
            });
        }
    });
});
