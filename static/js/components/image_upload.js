function showImageError(container, message) {
    const errorContainer = container.querySelector('.image-upload-errors');
    if (!errorContainer) return;

    errorContainer.innerHTML = '';

    const p = document.createElement('p');
    p.className = 'image-upload-error';

    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute('class', 'image-upload-error-icon');
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

    const dropzone = container.querySelector('.image-upload-dropzone');
    if (dropzone) {
        dropzone.classList.add('image-upload-dropzone-error');
    }
}

function clearImageError(container) {
    const errorContainer = container.querySelector('.image-upload-errors');
    if (errorContainer) {
        errorContainer.innerHTML = '';
    }

    const dropzone = container.querySelector('.image-upload-dropzone');
    if (dropzone) {
        dropzone.classList.remove('image-upload-dropzone-error');
    }
}

function setupImageUpload(fieldId) {
    const input = document.getElementById(fieldId);
    if (!input) return;

    const container = input.closest('.image-upload-container');
    const dropzone = container ? container.querySelector('.image-upload-dropzone') : null;

    // Handle file selection and preview
    input.addEventListener('change', function (e) {
        if (e.target.files && e.target.files[0]) {
            const reader = new FileReader();
            reader.onload = function (e) {
                const preview = document.getElementById('preview-' + fieldId);
                const placeholder = document.getElementById('placeholder-' + fieldId);
                if (preview && placeholder) {
                    preview.src = e.target.result;
                    preview.classList.remove('hidden');
                    placeholder.classList.add('hidden');
                }
            }
            reader.readAsDataURL(e.target.files[0]);

            // Clear error if present
            if (container) {
                clearImageError(container);
            }
        } else {
            // Handle clearing variables if no file selected
            const preview = document.getElementById('preview-' + fieldId);
            const placeholder = document.getElementById('placeholder-' + fieldId);
            if (preview && placeholder) {
                preview.src = '#';
                preview.classList.add('hidden');
                placeholder.classList.remove('hidden');
            }
            // Re-validate if required
            if (input.required && container) {
                showImageError(container, 'This field is required.');
            }
        }
    });

    // Handle form submission validation
    const form = input.closest('form');
    if (form) {
        if (!form.hasImageUploadValidation) {
            form.hasImageUploadValidation = true;

            form.addEventListener('submit', function (e) {
                let hasError = false;
                form.querySelectorAll('input[type="file"]').forEach(fileInput => {
                    const fileContainer = fileInput.closest('.image-upload-container');
                    if (fileContainer && fileInput.required && (!fileInput.files || fileInput.files.length === 0)) {
                        hasError = true;
                        showImageError(fileContainer, 'This field is required.');

                        if (fileInput === form.querySelectorAll('input[type="file"]:required:invalid')[0]) {
                            fileInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                    }
                });

                if (hasError) {
                    e.preventDefault();
                }
            });
        }
    }
}
