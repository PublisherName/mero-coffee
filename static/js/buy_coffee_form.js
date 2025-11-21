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
    amountButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            const amount = this.getAttribute('data-amount');
            amountInput.value = amount;
            updateSubmitButton(amount);
            clearError('amount-error');

            // Visual feedback
            amountButtons.forEach(b => b.classList.remove('border-red-500', 'bg-red-500/20'));
            this.classList.add('border-red-500', 'bg-red-500/20');
        });
    });

    // Custom amount input handler
    amountInput.addEventListener('input', function () {
        const amount = parseInt(this.value) || 0;
        updateSubmitButton(amount);
        validateAmount();

        // Remove all button selections when custom amount is entered
        amountButtons.forEach(b => {
            b.classList.remove('border-red-500', 'bg-red-500/20', 'border-orange-500', 'bg-orange-500/20');
            b.classList.add('border-slate-700');
        });
    });

    // Anonymous checkbox handler
    anonymousCheckbox.addEventListener('change', function () {
        if (this.checked) {
            nameInput.value = '';
            nameInput.disabled = true;
            nameInput.classList.add('opacity-50', 'cursor-not-allowed');
            clearError('name-error');
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
            // Remove all check icons and reset borders
            document.querySelectorAll('.payment-check-icon').forEach(icon => icon.classList.add('hidden'));
            document.querySelectorAll('.payment-provider-label > div').forEach(div => {
                div.classList.remove('border-green-500', 'border-purple-500', 'shadow-green-500/50', 'shadow-purple-500/50');
                div.classList.add('border-slate-700');
            });

            // Get the inner div and check icon for this label
            const innerDiv = this.querySelector('div');
            const checkIcon = this.querySelector('.payment-check-icon');
            const value = paymentInputs[index].value;

            // Show check icon
            if (checkIcon) {
                checkIcon.classList.remove('hidden');
            }

            // Apply selected styling
            if (value === 'esewa') {
                innerDiv.classList.remove('border-slate-700');
                innerDiv.classList.add('border-green-500', 'shadow-green-500/50');
            } else {
                innerDiv.classList.remove('border-slate-700');
                innerDiv.classList.add('border-purple-500', 'shadow-purple-500/50');
            }

            clearError('payment-error');
        });
    });

    // Validation functions
    function validateAmount() {
        const amount = parseInt(amountInput.value) || 0;
        if (amount < coffeePrice) {
            showError('amount-error', `Amount must be at least Rs. ${coffeePrice}`);
            return false;
        }
        clearError('amount-error');
        return true;
    }

    function validateName() {
        if (!anonymousCheckbox.checked && !nameInput.value.trim()) {
            showError('name-error', 'Name is required unless you choose to remain anonymous');
            return false;
        }
        clearError('name-error');
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
        errorElement.textContent = message;
        errorElement.classList.remove('hidden');
    }

    function clearError(elementId) {
        const errorElement = document.getElementById(elementId);
        errorElement.textContent = '';
        errorElement.classList.add('hidden');
    }

    function updateSubmitButton(amount) {
        submitAmountSpan.textContent = amount || coffeePrice;
    }

    // Form submission
    form.addEventListener('submit', function (e) {
        e.preventDefault();

        // Validate all fields
        const isAmountValid = validateAmount();
        const isNameValid = validateName();
        const isPaymentValid = validatePaymentProvider();

        if (isAmountValid && isNameValid && isPaymentValid) {
            // All validations passed, submit the form
            this.submit();
        } else {
            // Scroll to first error
            const firstError = document.querySelector('.text-red-400:not(.hidden)');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    });

    // Initialize with default amount
    updateSubmitButton(coffeePrice);
});
