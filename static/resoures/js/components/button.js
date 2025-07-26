class ButtonType {
    static DANGER = 'danger';
    static WARNING = 'warning';
    static SUCCESS = 'success';
    static INFO = 'info';
}

class CustomSubmitButton extends HTMLElement {
    connectedCallback() {
        // === Get attributes from the custom element ===
        const label = this.getAttribute('label') || 'Submit';
        const formId = this.getAttribute('form-id');
        const url = this.getAttribute('post'); // AJAX POST URL
        const method = this.getAttribute('method') || 'POST';
        const showSpinner = this.getAttribute('showspinner') === 'true';
        const buttonType = this.getAttribute('buttontype') || ButtonType.WARNING;
        
        // Confirmation settings
        const confirmMessage = this.getAttribute('confirm-message') || 'Are you sure you want to delete this item? This action cannot be undone.';
        const confirmTitle = this.getAttribute('confirm-title') || 'Confirm Delete';
        const skipConfirmation = this.getAttribute('skip-confirmation') === 'true';

        // === Create actual <button> ===
        const button = document.createElement('button');
        button.type = 'button'; // Not submit to prevent default submission
        button.className = `btn btn-${buttonType}`;

        // Add extra classes if any
        const extraClasses = this.getAttribute('class');
        if (extraClasses) {
            button.classList.add(...extraClasses.split(' '));
        }

        // === Button Content ===
        const textSpan = document.createElement('span');
        textSpan.textContent = label;
        textSpan.className = 'button-text';
        button.appendChild(textSpan);

        const spinner = document.createElement('span');
        spinner.className = 'spinner-border spinner-border-sm ms-2 d-none';
        spinner.setAttribute('role', 'status');
        spinner.setAttribute('aria-hidden', 'true');
        if (showSpinner) button.appendChild(spinner);

        this.innerHTML = ''; // Clear existing content
        this.appendChild(button);

        // === Handle click and submit via AJAX ===
        button.addEventListener('click', async (e) => {
            // Check if this is a delete action and needs confirmation
            const needsConfirmation = !skipConfirmation && label.toLowerCase().includes('delete');
            
            if (needsConfirmation) {
                const confirmed = await this.showConfirmationDialog(confirmTitle, confirmMessage);
                if (!confirmed) {
                    return; // User cancelled, don't proceed
                }
            }

            const form = document.getElementById(formId);
            if (!form) {
                console.error(`Form with id "${formId}" not found.`);
                return;
            }

            const formData = new FormData(form);
            textSpan.textContent = 'Saving...';
            spinner.classList.remove('d-none');
            button.disabled = true;

            try {
                const response = await fetch(url, {
                    method: method.toUpperCase(),
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                });

                const result = await response.text(); // or .json()
                console.log('AJAX form submit success:', result);

                // OPTIONAL: Replace element with new HTML from response
                const targetSelector = this.getAttribute('target');
                if (targetSelector) {
                    const target = document.querySelector(targetSelector);
                    if (target) target.innerHTML = result;
                }

            } catch (err) {
                console.error('AJAX submit failed:', err);
            } finally {
                textSpan.textContent = label;
                spinner.classList.add('d-none');
                button.disabled = false;
            }
        });
    }

    // Show confirmation dialog - returns a Promise that resolves to boolean
    showConfirmationDialog(title, message) {
        return new Promise((resolve) => {
            // Check if Bootstrap modal is available, otherwise use native confirm
            if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                this.showBootstrapModal(title, message, resolve);
            } else {
                // Fallback to native confirm dialog
                resolve(confirm(`${title}\n\n${message}`));
            }
        });
    }

    // Create and show Bootstrap modal for confirmation
    showBootstrapModal(title, message, resolve) {
        // Create modal HTML
        const modalId = `confirmModal_${Math.random().toString(36).substr(2, 9)}`;
        const modalHtml = `
            <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="${modalId}Label">${title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            ${message}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-danger confirm-delete-btn">Delete</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add modal to DOM
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modalElement = document.getElementById(modalId);
        const modal = new bootstrap.Modal(modalElement);

        // Handle confirm button click
        const confirmBtn = modalElement.querySelector('.confirm-delete-btn');
        confirmBtn.addEventListener('click', () => {
            modal.hide();
            resolve(true);
        });

        // Handle modal close (cancel)
        modalElement.addEventListener('hidden.bs.modal', () => {
            modalElement.remove(); // Clean up DOM
            resolve(false);
        }, { once: true });

        // Show the modal
        modal.show();
    }
}

// Register it
customElements.define("custom-button", CustomSubmitButton);