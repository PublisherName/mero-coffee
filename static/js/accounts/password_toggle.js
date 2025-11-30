/**
 * Password Toggle Utility
 * Adds show/hide password functionality to password input fields
 */

/**
 * Initialize password toggle functionality for a password field
 * @param {string} fieldId - The ID of the password input field
 */
function initPasswordToggle(fieldId) {
    const passwordField = document.getElementById(fieldId);
    if (!passwordField) {
        console.warn(`Password field with ID "${fieldId}" not found`);
        return;
    }

    // Check if already wrapped
    if (passwordField.parentElement.classList.contains('password-field-wrapper')) {
        return;
    }

    // Create wrapper
    const wrapper = document.createElement('div');
    wrapper.className = 'password-field-wrapper';

    // Wrap the password field
    passwordField.parentNode.insertBefore(wrapper, passwordField);
    wrapper.appendChild(passwordField);

    // Create toggle button
    const toggleBtn = document.createElement('button');
    toggleBtn.type = 'button';
    toggleBtn.className = 'password-toggle-btn';
    toggleBtn.setAttribute('aria-label', 'Toggle password visibility');
    toggleBtn.innerHTML = getEyeIcon(false);

    // Add click event
    toggleBtn.addEventListener('click', function () {
        const isPassword = passwordField.type === 'password';
        passwordField.type = isPassword ? 'text' : 'password';
        toggleBtn.innerHTML = getEyeIcon(isPassword);
        toggleBtn.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');
    });

    // Append toggle button to wrapper
    wrapper.appendChild(toggleBtn);
}

/**
 * Get SVG icon for eye (show/hide)
 * @param {boolean} isVisible - Whether password is currently visible
 * @returns {string} SVG icon HTML
 */
function getEyeIcon(isVisible) {
    if (isVisible) {
        // Eye icon (password is visible, show "hide" icon)
        return `
            <svg class="password-toggle-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
            </svg>
        `;
    } else {
        // Eye-off icon (password is hidden, show "show" icon)
        return `
            <svg class="password-toggle-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88"></path>
            </svg>
        `;
    }
}

/**
 * Initialize password toggle for multiple fields
 * @param {string[]} fieldIds - Array of password field IDs
 */
function initPasswordToggles(fieldIds) {
    fieldIds.forEach(fieldId => initPasswordToggle(fieldId));
}

// Export functions for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { initPasswordToggle, initPasswordToggles };
}
