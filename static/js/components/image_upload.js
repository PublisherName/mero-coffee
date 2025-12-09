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
            if (container && dropzone) {
                const error = container.querySelector('.client-error');
                if (error) error.remove();
                dropzone.classList.remove('image-upload-dropzone-error');
            }
        } else {
            // Handle clearing variables if no file selected (or selection cancelled resulting in empty input)
            const preview = document.getElementById('preview-' + fieldId);
            const placeholder = document.getElementById('placeholder-' + fieldId);
            if (preview && placeholder) {
                preview.src = '#';
                preview.classList.add('hidden');
                placeholder.classList.remove('hidden');
            }
        }
    });

    // Handle form submission validation
    const form = input.closest('form');
    if (form) {
        // Use a custom property to avoid adding multiple listeners to the same form
        if (!form.hasImageUploadValidation) {
            form.hasImageUploadValidation = true;

            form.addEventListener('submit', function (e) {
                let hasError = false;
                form.querySelectorAll('input[type="file"]').forEach(fileInput => {
                    // Check if it's an image upload component input
                    const fileContainer = fileInput.closest('.image-upload-container');
                    if (fileContainer && fileInput.required && (!fileInput.files || fileInput.files.length === 0)) {
                        hasError = true;

                        const fileDropzone = fileContainer.querySelector('.image-upload-dropzone');
                        if (fileDropzone) {
                            fileDropzone.classList.add('image-upload-dropzone-error');
                        }

                        let error = fileContainer.querySelector('.client-error');
                        if (!error) {
                            error = document.createElement('p');
                            error.className = 'image-upload-error client-error';
                            const errorsContainer = fileContainer.querySelector('.image-upload-errors');
                            if (errorsContainer) {
                                errorsContainer.appendChild(error);
                            } else {
                                // Create errors container if it doesn't exist
                                const newErrorsContainer = document.createElement('div');
                                newErrorsContainer.className = 'image-upload-errors';
                                newErrorsContainer.appendChild(error);
                                fileContainer.appendChild(newErrorsContainer);
                            }
                        }
                        // Get label text
                        const label = fileContainer.querySelector('.image-upload-label');
                        const labelText = label ? label.textContent.replace('*', '').trim() : 'This field';
                        error.textContent = `${labelText} is required.`;

                        // Scroll to first error
                        if (hasError && fileInput === form.querySelectorAll('input[type="file"]:required:invalid')[0]) {
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
