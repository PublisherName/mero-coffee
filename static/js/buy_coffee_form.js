/**
 * Buy Coffee Form - Client-side validation and interactivity
 * Handles amount selection, validation, and payment provider selection
 */

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    // Get coffee price from data attribute
    const formElement = document.getElementById('buyCoffeeForm');
    if (!formElement) return; // Exit if form not found on page

    const coffeePrice = parseInt(formElement.dataset.coffeePrice);

    // DOM Elements
    const form = formElement;
    const amountInput = document.getElementById('custom_amount');
    const nameInput = document.getElementById('supporter_name');
    const anonymousCheckbox = document.getElementById('is_anonymous');
    const messageInput = document.getElementById('message');
    const submitAmountSpan = document.getElementById('submit-amount');
    const charCountSpan = document.getElementById('char-count');
    const amountButtons = document.querySelectorAll('.amount-btn');
    const paymentLabels = document.querySelectorAll('.payment-provider-label');
    const paymentInputs = document.querySelectorAll('.payment-provider-input');

    // Amount button handlers
    let selectedAmount = null;

    amountButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            const amount = this.getAttribute('data-amount');
            selectedAmount = amount;

            // Clear input visual value but keep track for submit
            amountInput.value = '';

            updateSubmitButton(amount);

            if (typeof clearNumberError === 'function') {
                clearNumberError(amountInput);
            }

            // Visual feedback - Use .selected class and direct styles
            // Reset all
            amountButtons.forEach(b => {
                b.classList.remove('selected', 'border-red-500', 'bg-red-500/20');
                b.classList.add('border-slate-700');
            });

            // Set active
            this.classList.add('selected', 'border-red-500', 'bg-red-500/20');
            this.classList.remove('border-slate-700');
        });
    });

    // Custom amount input handler
    amountInput.addEventListener('input', function () {
        selectedAmount = null; // Clear selected button state
        const amount = parseInt(this.value) || 0;
        updateSubmitButton(amount);
        validateAmount(); // This now validates the input value directly

        // Remove all button selections
        amountButtons.forEach(b => {
            b.classList.remove('selected', 'border-red-500', 'bg-red-500/20', 'border-orange-500', 'bg-orange-500/20');
            b.classList.add('border-slate-700');
        });
    });

    // Anonymous checkbox handler
    anonymousCheckbox.addEventListener('change', function () {
        if (this.checked) {
            nameInput.value = '';
            nameInput.disabled = true;
            nameInput.classList.add('opacity-50', 'cursor-not-allowed');
            if (typeof clearTextError === 'function') {
                clearTextError(nameInput);
            }
        } else {
            nameInput.disabled = false;
            nameInput.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    });

    // Message character counter
    messageInput.addEventListener('input', function () {
        charCountSpan.textContent = this.value.length;
    });

    // Payment provider selection
    paymentLabels.forEach((label, index) => {
        label.addEventListener('click', function () {
            clearError('payment-error');

            // Get the payment card and its brand color
            const paymentCard = this.querySelector('.payment-provider-card');
            const brandColor = getComputedStyle(paymentCard).getPropertyValue('--brand-color').trim();

            // Apply selected styling with brand color
            if (brandColor) {
                paymentCard.style.boxShadow = `0 10px 15px -3px ${brandColor}33`;
            }
        });
    });

    // Remove shadow when payment is deselected (on other payment click)
    paymentInputs.forEach(input => {
        input.addEventListener('change', function () {
            // Remove shadow from all cards
            document.querySelectorAll('.payment-provider-card').forEach(card => {
                card.style.boxShadow = '';
            });

            // Add shadow to selected card
            if (this.checked) {
                const paymentCard = this.nextElementSibling;
                const brandColor = getComputedStyle(paymentCard).getPropertyValue('--brand-color').trim();
                if (brandColor) {
                    paymentCard.style.boxShadow = `0 10px 15px -3px ${brandColor}33`;
                }
            }
        });
    });

    // Validation functions
    function validateAmount() {
        const amount = parseInt(amountInput.value) || 0;
        if (amount < coffeePrice) {
            // Use component's showNumberError if available
            if (typeof showNumberError === 'function') {
                showNumberError(amountInput, `Amount must be at least Rs. ${coffeePrice}`);
            }
            return false;
        }
        if (typeof clearNumberError === 'function') {
            clearNumberError(amountInput);
        }
        return true;
    }

    function validateName() {
        if (!anonymousCheckbox.checked && !nameInput.value.trim()) {
            if (typeof showTextError === 'function') {
                showTextError(nameInput, 'Name is required unless you choose to remain anonymous');
            }
            return false;
        }
        if (typeof clearTextError === 'function') {
            clearTextError(nameInput);
        }
        return true;
    }

    function validatePaymentProvider() {
        const selected = document.querySelector('.payment-provider-input:checked');
        if (!selected) {
            showError('payment-error', 'Please select a payment method');
            return false;
        }
        clearError('payment-error');
        return true;
    }

    function showError(elementId, message) {
        const errorElement = document.getElementById(elementId);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.remove('hidden');
        }
    }

    function clearError(elementId) {
        const errorElement = document.getElementById(elementId);
        if (errorElement) {
            errorElement.textContent = '';
            errorElement.classList.add('hidden');
        }
    }

    function updateSubmitButton(amount) {
        submitAmountSpan.textContent = amount || coffeePrice;
    }

    // Form submission
    form.addEventListener('submit', function (e) {
        e.preventDefault();

        // If a button is selected but input is empty, fill it
        if (selectedAmount && !amountInput.value) {
            amountInput.value = selectedAmount;
        }

        // Validate all fields
        const isAmountValid = validateAmount();
        const isNameValid = validateName();
        const isPaymentValid = validatePaymentProvider();

        if (isAmountValid && isNameValid && isPaymentValid) {
            // All validations passed, submit the form
            this.submit();
        } else {
            // Scroll to first error
            const firstError = document.querySelector('.number-input-error, .text_input-error, .textarea-input-error, .image-upload-error, .text-red-400:not(.hidden)');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    });

    // Initialize with default amount
    updateSubmitButton(coffeePrice);
});
