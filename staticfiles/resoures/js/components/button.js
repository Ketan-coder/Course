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

        // Icon settings
        const customIcon = this.getAttribute('icon');
        const iconColor = this.getAttribute('icon-color') || '';
        const iconPosition = this.getAttribute('icon-position') || 'start'; // 'start' or 'end'
        const iconSize = this.getAttribute('icon-size') || '14'; // default size
        const disableAutoIcon = this.getAttribute('disable-auto-icon') === 'true';

        // === Create actual <button> ===
        const button = document.createElement('button');
        button.type = 'button'; // Not submit to prevent default submission
        button.className = `btn btn-${buttonType}`;

        // Add extra classes if any
        const extraClasses = this.getAttribute('class');
        if (extraClasses) {
            button.classList.add(...extraClasses.split(' '));
        }

        // === Button Content with Icon Support ===
        const textSpan = document.createElement('span');
        textSpan.className = 'button-text';
        
        // Determine which icon to use
        const iconName = this.getIconName(customIcon, label, disableAutoIcon);
        
        // Create button content with icon
        this.createButtonContent(textSpan, label, iconName, iconColor, iconPosition, iconSize);
        
        button.appendChild(textSpan);

        const spinner = document.createElement('span');
        spinner.className = 'spinner-border spinner-border-sm ms-2 d-none';
        spinner.setAttribute('role', 'status');
        spinner.setAttribute('aria-hidden', 'true');
        if (showSpinner) button.appendChild(spinner);

        this.innerHTML = ''; // Clear existing content
        this.appendChild(button);

        // Add CSS for proper icon alignment
        const style = document.createElement('style');
        style.textContent = `
            .button-text {
                display: inline-flex;
                align-items: center;
                gap: 0.375rem;
            }
            .button-text i {
                display: inline-flex;
                align-items: center;
                vertical-align: middle;
                line-height: 1;
            }
        `;
        this.appendChild(style);

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
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                console.log('AJAX form submit success:', result);
                location.reload(); // Reload the page to reflect changes

                // OPTIONAL: Replace element with new HTML from response
                const targetSelector = this.getAttribute('target');
                if (targetSelector) {
                    const target = document.querySelector(targetSelector);
                    if (target) target.innerHTML = result;
                }

            } catch (err) {
                console.error('AJAX submit failed:', err);
            } finally {
                // Restore original button content
                textSpan.innerHTML = '';
                this.createButtonContent(textSpan, label, iconName, iconColor, iconPosition, iconSize);
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

    // Get the appropriate icon name based on custom icon, label, or auto-detection
    getIconName(customIcon, label, disableAutoIcon) {
        // If custom icon is provided, use it
        if (customIcon) {
            return customIcon;
        }

        // If auto-icon is disabled, return null
        if (disableAutoIcon) {
            return null;
        }

        // Auto-detect icon based on label
        const labelLower = label.toLowerCase();
        
        // Delete actions
        if (labelLower.includes('delete') || labelLower.includes('remove') || labelLower.includes('trash')) {
            return 'trash';
        }
        
        // Edit/Update actions
        if (labelLower.includes('edit') || labelLower.includes('update') || labelLower.includes('modify')) {
            return 'pencil-simple';
        }
        
        // Save actions
        if (labelLower.includes('save') || labelLower.includes('store')) {
            return 'floppy-disk';
        }
        
        // Create/Add actions
        if (labelLower.includes('create') || labelLower.includes('add') || labelLower.includes('new')) {
            return 'plus';
        }
        
        // Submit actions
        if (labelLower.includes('submit') || labelLower.includes('send')) {
            return 'paper-plane-tilt';
        }
        
        // Download actions
        if (labelLower.includes('download') || labelLower.includes('export')) {
            return 'download-simple';
        }
        
        // Upload actions
        if (labelLower.includes('upload') || labelLower.includes('import')) {
            return 'upload-simple';
        }
        
        // Search actions
        if (labelLower.includes('search') || labelLower.includes('find')) {
            return 'magnifying-glass';
        }
        
        // View actions
        if (labelLower.includes('view') || labelLower.includes('show') || labelLower.includes('preview')) {
            return 'eye';
        }
        
        // Copy actions
        if (labelLower.includes('copy') || labelLower.includes('duplicate')) {
            return 'copy';
        }
        
        // Print actions
        if (labelLower.includes('print')) {
            return 'printer';
        }
        
        // Cancel actions
        if (labelLower.includes('cancel') || labelLower.includes('close')) {
            return 'x';
        }
        
        // Confirm/OK actions
        if (labelLower.includes('confirm') || labelLower.includes('ok') || labelLower.includes('yes')) {
            return 'check';
        }
        
        // Refresh/Reload actions
        if (labelLower.includes('refresh') || labelLower.includes('reload')) {
            return 'arrow-clockwise';
        }
        
        // Default fallback
        return null;
    }

    // Create button content with icon and text
    createButtonContent(container, label, iconName, iconColor, iconPosition, iconSize) {
        container.innerHTML = ''; // Clear existing content
        
        if (!iconName) {
            // No icon, just text
            container.textContent = label;
            return;
        }

        // Create icon element
        const icon = document.createElement('i');
        icon.className = `ph ph-${iconName} ph-bold p-1`;
        icon.style.fontSize = `${iconSize}px`;
        icon.style.lineHeight = '1';
        icon.style.display = 'inline-flex';
        icon.style.alignItems = 'center';
        
        if (iconColor) {
            icon.style.color = iconColor;
        }

        // Create text span for better control
        const textSpan = document.createElement('span');
        textSpan.textContent = label;
        textSpan.style.display = 'inline-flex';
        textSpan.style.alignItems = 'center';

        // Clear container and set up flexbox
        container.style.display = 'inline-flex';
        container.style.alignItems = 'center';
        container.style.gap = '0.375rem';

        // Position icon based on iconPosition
        if (iconPosition === 'end') {
            container.appendChild(textSpan);
            container.appendChild(icon);
        } else {
            // Default to start
            container.appendChild(icon);
            container.appendChild(textSpan);
        }
    }
}

// Register it
customElements.define("custom-button", CustomSubmitButton);