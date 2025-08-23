class ButtonType {
    static DANGER = 'danger';
    static WARNING = 'warning';
    static SUCCESS = 'success';
    static INFO = 'info';
    static PRIMARY = 'primary';
    static SECONDARY = 'secondary';
}

class IconButton extends HTMLElement {
    connectedCallback() {
        const icon = this.getAttribute('icon') || 'circle';
        const variant = this.getAttribute('variant') || this.getAttribute('buttontype') || 'primary';
        const size = this.getAttribute('size') || 'md';
        const disabled = this.hasAttribute('disabled');
        const loading = this.hasAttribute('loading');
        const iconWeight = this.getAttribute('icon-weight') || 'regular';
        const text = this.getAttribute('text') || this.getAttribute('label') || '';
        const tooltip = this.getAttribute('tooltip') || '';
        const rounded = this.getAttribute('rounded') || 'default';
        const shadow = this.hasAttribute('shadow');
        const isGhost = this.hasAttribute('is_ghost');
        const showSpinner = this.getAttribute('showspinner') === 'true' || true;
        
        // AJAX attributes
        const formId = this.getAttribute('form-id');
        const postUrl = this.getAttribute('post');
        const method = this.getAttribute('method') || 'POST';
        const target = this.getAttribute('target');
        const successMessage = this.getAttribute('success-message');
        const errorMessage = this.getAttribute('error-message');
        
        // Event handlers
        const onClickFn = this.getAttribute('data-onclick');
        const onHoverFn = this.getAttribute('data-onhover');
        const onFocusFn = this.getAttribute('data-onfocus');
        const onSuccessFn = this.getAttribute('data-onsuccess');
        const onErrorFn = this.getAttribute('data-onerror');

        // Determine final variant
        const finalVariant = isGhost ? 'ghost' : variant;

        // Create button structure
        this.innerHTML = `
            <button class="icon-btn icon-btn-${finalVariant} icon-btn-${size} ${rounded !== 'default' ? `icon-btn-${rounded}` : ''} ${shadow ? 'icon-btn-shadow' : ''}" 
                    ${disabled ? 'disabled' : ''} 
                    ${tooltip ? `title="${tooltip}"` : ''}
                    type="button">
                <i class="ph ${loading ? 'ph-spinner' : `ph-${icon}`}" 
                   data-weight="${loading ? 'bold' : iconWeight}"></i>
                ${text ? `<span class="btn-text">${text}</span>` : ''}
                ${showSpinner ? '<span class="spinner-border spinner-border-sm ms-2 d-none" role="status" aria-hidden="true"></span>' : ''}
                ${loading ? '<div class="loading-overlay"></div>' : ''}
            </button>
        `;

        const button = this.querySelector('.icon-btn');
        const iconEl = this.querySelector('i');
        const textEl = this.querySelector('.btn-text');
        const spinner = this.querySelector('.spinner-border');

        // Store original text for loading states
        this.originalText = text;
        this.originalIcon = icon;

        // Set icon weight attribute for Phosphor icons
        if (!loading) {
            iconEl.setAttribute('data-weight', iconWeight);
        }

        // Attach event listeners
        this.attachEvents(button, textEl, spinner, onClickFn, onHoverFn, onFocusFn, onSuccessFn, onErrorFn, {
            formId, postUrl, method, target, successMessage, errorMessage
        });

        // Add default styles
        this.addStyles();

        // Load Phosphor icons if not already loaded
        this.loadPhosphorIcons();
    }

    attachEvents(button, textEl, spinner, onClickFn, onHoverFn, onFocusFn, onSuccessFn, onErrorFn, ajaxConfig) {
        button.addEventListener('click', async (e) => {
            if (button.disabled || this.hasAttribute('loading')) return;
            
            // Add ripple effect
            this.createRipple(e, button);
            
            // Handle AJAX form submission if configured
            if (ajaxConfig.formId && ajaxConfig.postUrl) {
                await this.handleAjaxSubmit(button, textEl, spinner, ajaxConfig, onSuccessFn, onErrorFn);
            }
            
            // Call custom click handler
            if (onClickFn && window[onClickFn]) {
                window[onClickFn](e);
            }
        });

        button.addEventListener('mouseenter', (e) => {
            if (onHoverFn && window[onHoverFn]) {
                window[onHoverFn](e);
            }
        });

        button.addEventListener('focus', (e) => {
            if (onFocusFn && window[onFocusFn]) {
                window[onFocusFn](e);
            }
        });
    }

    async handleAjaxSubmit(button, textEl, spinner, config, onSuccessFn, onErrorFn) {
        const form = document.getElementById(config.formId);
        if (!form) {
            console.error(`Form with id "${config.formId}" not found.`);
            this.showError(config.errorMessage || 'Form not found');
            return;
        }

        const formData = new FormData(form);
        
        // Set loading state
        this.setLoadingState(true, textEl, spinner);

        try {
            const response = await fetch(config.postUrl, {
                method: config.method.toUpperCase(),
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.text();
            console.log('AJAX form submit success:', result);

            // Update target element if specified
            if (config.target) {
                const targetElement = document.querySelector(config.target);
                if (targetElement) {
                    targetElement.innerHTML = result;
                }
            }

            // Show success message
            if (config.successMessage) {
                this.showSuccess(config.successMessage);
            }

            // Call custom success handler
            if (onSuccessFn && window[onSuccessFn]) {
                window[onSuccessFn](result);
            }

        } catch (err) {
            console.error('AJAX submit failed:', err);
            
            // Show error message
            if (config.errorMessage) {
                this.showError(config.errorMessage);
            }

            // Call custom error handler
            if (onErrorFn && window[onErrorFn]) {
                window[onErrorFn](err);
            }
        } finally {
            // Reset loading state
            this.setLoadingState(false, textEl, spinner);
        }
    }

    setLoadingState(loading, textEl, spinner) {
        const button = this.querySelector('.icon-btn');
        const iconEl = this.querySelector('i');

        if (loading) {
            button.disabled = true;
            if (textEl) textEl.textContent = 'Processing...';
            if (spinner) spinner.classList.remove('d-none');
            if (iconEl) {
                iconEl.className = 'ph ph-spinner';
                iconEl.setAttribute('data-weight', 'bold');
            }
        } else {
            button.disabled = false;
            if (textEl) textEl.textContent = this.originalText;
            if (spinner) spinner.classList.add('d-none');
            if (iconEl) {
                iconEl.className = `ph ph-${this.originalIcon}`;
                iconEl.setAttribute('data-weight', this.getAttribute('icon-weight') || 'regular');
            }
        }
    }

    showSuccess(message) {
        this.showToast(message, 'success');
    }

    showError(message) {
        this.showToast(message, 'error');
    }

    showToast(message, type) {
        // Create a simple toast notification
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        toast.textContent = message;
        
        const toastStyles = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 6px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
        `;
        
        toast.style.cssText = toastStyles;
        toast.style.background = type === 'success' ? '#10b981' : '#ef4444';
        
        document.body.appendChild(toast);
        
        // Animate in
        requestAnimationFrame(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateX(0)';
        });
        
        // Remove after 3 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    createRipple(event, button) {
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;

        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple');

        button.appendChild(ripple);

        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    loadPhosphorIcons() {
        if (!document.querySelector('link[href*="phosphor"]')) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'https://cdnjs.cloudflare.com/ajax/libs/phosphor-icons/2.0.2/phosphor.min.css';
            document.head.appendChild(link);
        }
    }

    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .icon-btn {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
                border: none;
                cursor: pointer;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                font-weight: 500;
                text-decoration: none;
                position: relative;
                overflow: hidden;
                transition: all 0.2s ease-in-out;
                outline: none;
                white-space: nowrap;
            }

            /* Sizes */
            .icon-btn-xs {
                padding: 0.25rem;
                font-size: 0.75rem;
                min-width: 1.5rem;
                min-height: 1.5rem;
            }

            .icon-btn-sm {
                padding: 0.375rem 0.5rem;
                font-size: 0.875rem;
                min-width: 2rem;
                min-height: 2rem;
            }

            .icon-btn-md {
                padding: 0.5rem 0.75rem;
                font-size: 1rem;
                min-width: 2.5rem;
                min-height: 2.5rem;
            }

            .icon-btn-lg {
                padding: 0.75rem 1rem;
                font-size: 1.125rem;
                min-width: 3rem;
                min-height: 3rem;
            }

            .icon-btn-xl {
                padding: 1rem 1.25rem;
                font-size: 1.25rem;
                min-width: 3.5rem;
                min-height: 3.5rem;
            }

            /* Variants */
            .icon-btn-primary {
                background: #3b82f6;
                color: white;
                border-radius: 0.375rem;
            }

            .icon-btn-primary:hover:not(:disabled) {
                background: #2563eb;
                transform: translateY(-1px);
            }

            .icon-btn-secondary {
                background: #6b7280;
                color: white;
                border-radius: 0.375rem;
            }

            .icon-btn-secondary:hover:not(:disabled) {
                background: #4b5563;
                transform: translateY(-1px);
            }

            .icon-btn-success {
                background: #10b981;
                color: white;
                border-radius: 0.375rem;
            }

            .icon-btn-success:hover:not(:disabled) {
                background: #059669;
                transform: translateY(-1px);
            }

            .icon-btn-danger {
                background: #ef4444;
                color: white;
                border-radius: 0.375rem;
            }

            .icon-btn-danger:hover:not(:disabled) {
                background: #dc2626;
                transform: translateY(-1px);
            }

            .icon-btn-warning {
                background: #f59e0b;
                color: white;
                border-radius: 0.375rem;
            }

            .icon-btn-warning:hover:not(:disabled) {
                background: #d97706;
                transform: translateY(-1px);
            }

            .icon-btn-info {
                background: #0ea5e9;
                color: white;
                border-radius: 0.375rem;
            }

            .icon-btn-info:hover:not(:disabled) {
                background: #0284c7;
                transform: translateY(-1px);
            }

            .icon-btn-ghost {
                background: transparent;
                color: #374151;
                border: 1px solid #d1d5db;
                border-radius: 0.375rem;
            }

            .icon-btn-ghost:hover:not(:disabled) {
                background: #f3f4f6;
                border-color: #9ca3af;
            }

            .icon-btn-outline {
                background: transparent;
                color: #3b82f6;
                border: 2px solid #3b82f6;
                border-radius: 0.375rem;
            }

            .icon-btn-outline:hover:not(:disabled) {
                background: #3b82f6;
                color: white;
            }

            /* Rounded variants */
            .icon-btn-rounded {
                border-radius: 0.75rem !important;
            }

            .icon-btn-pill {
                border-radius: 9999px !important;
            }

            .icon-btn-square {
                border-radius: 0 !important;
            }

            /* Shadow */
            .icon-btn-shadow {
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            }

            .icon-btn-shadow:hover:not(:disabled) {
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            }

            /* Disabled state */
            .icon-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: none !important;
            }

            /* Loading state */
            .icon-btn:has(.loading-overlay) {
                pointer-events: none;
            }

            .loading-overlay {
                position: absolute;
                inset: 0;
                background: rgba(255, 255, 255, 0.1);
                border-radius: inherit;
            }

            .ph-spinner {
                animation: spin 1s linear infinite;
            }

            .spinner-border {
                display: inline-block;
                width: 1rem;
                height: 1rem;
                vertical-align: text-bottom;
                border: 0.125em solid currentColor;
                border-right-color: transparent;
                border-radius: 50%;
                animation: spinner-border 0.75s linear infinite;
            }

            .spinner-border-sm {
                width: 0.75rem;
                height: 0.75rem;
                border-width: 0.1em;
            }

            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }

            @keyframes spinner-border {
                to { transform: rotate(360deg); }
            }

            /* Focus states */
            .icon-btn:focus-visible {
                outline: 2px solid #3b82f6;
                outline-offset: 2px;
            }

            /* Ripple effect */
            .ripple {
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.6);
                transform: scale(0);
                animation: ripple 0.6s linear;
                pointer-events: none;
            }

            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }

            /* Text spacing */
            .btn-text {
                line-height: 1;
            }

            /* Utility classes */
            .d-none {
                display: none !important;
            }

            .ms-2 {
                margin-left: 0.5rem;
            }

            /* Dark mode support */
            @media (prefers-color-scheme: dark) {
                .icon-btn-ghost {
                    color: #f3f4f6;
                    border-color: #4b5563;
                }
                
                .icon-btn-ghost:hover:not(:disabled) {
                    background: #374151;
                    border-color: #6b7280;
                }
            }
        `;
        this.appendChild(style);
    }

    // Public methods for dynamic updates
    setIcon(iconName) {
        const iconEl = this.querySelector('i');
        if (iconEl && !this.hasAttribute('loading')) {
            iconEl.className = `ph ph-${iconName}`;
            this.originalIcon = iconName;
        }
    }

    setLoading(loading) {
        const textEl = this.querySelector('.btn-text');
        const spinner = this.querySelector('.spinner-border');
        this.setLoadingState(loading, textEl, spinner);
    }

    setText(text) {
        const textEl = this.querySelector('.btn-text');
        if (textEl) {
            textEl.textContent = text;
            this.originalText = text;
        } else if (text) {
            // Add text if it doesn't exist
            const iconEl = this.querySelector('i');
            const span = document.createElement('span');
            span.className = 'btn-text';
            span.textContent = text;
            iconEl.parentNode.insertBefore(span, iconEl.nextSibling);
            this.originalText = text;
        }
    }

    // Submit form programmatically
    async submitForm() {
        const button = this.querySelector('.icon-btn');
        button.click();
    }
}

customElements.define('icon-button', IconButton);