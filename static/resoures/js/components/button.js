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
        button.addEventListener('click', async () => {
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
}

// Register it
customElements.define("custom-button", CustomSubmitButton);
