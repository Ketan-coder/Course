class ButtonType {
    static DANGER = 'danger';
    static WARNING = 'warning';
    static SUCCESS = 'success';
    static INFO = 'info';
}

class CustomSubmitButton extends HTMLElement {
    connectedCallback() {
        const label = this.getAttribute('label') || 'Submit';
        const type = this.getAttribute('type') || 'submit';
        const showSpinner = this.getAttribute('showspinner') === 'true';
        const buttonType = this.getAttribute('buttontype') || ButtonType.WARNING;

        const hxPost = this.getAttribute('post');
        const hxGet = this.getAttribute('get');
        const hxTarget = this.getAttribute('target') || 'this';
        const hxSwap = this.getAttribute('swap') || 'innerHTML';

        // Create <button> element
        const button = document.createElement('button');
        button.type = type;
        button.className = `btn btn-${buttonType}`;

        // Add extra classes from <custom-submit-button class="">
        const extraClasses = this.getAttribute('class');
        if (extraClasses) {
            button.classList.add(...extraClasses.split(' '));
        }

        // HTMX attributes
        if (hxPost) {
            button.setAttribute('hx-post', hxPost);
            button.setAttribute('hx-target', hxTarget);
            button.setAttribute('hx-swap', hxSwap);
        } else if (hxGet) {
            button.setAttribute('hx-get', hxGet);
            button.setAttribute('hx-target', hxTarget);
            button.setAttribute('hx-swap', hxSwap);
        }

        // Button content: label span + spinner span
        const labelSpan = document.createElement('span');
        labelSpan.className = 'button-text';
        labelSpan.textContent = label;

        const spinner = document.createElement('span');
        spinner.className = 'spinner-border spinner-border-sm ms-2 d-none';
        spinner.setAttribute('role', 'status');

        button.appendChild(labelSpan);
        if (showSpinner) button.appendChild(spinner);

        this.innerHTML = '';
        this.appendChild(button);

        // HTMX event binding
        const form = this.closest('form');
        if (form && showSpinner) {
            form.addEventListener('htmx:send', (e) => {
                const submitter = e.detail.elt;
                if (submitter === button) {
                    labelSpan.textContent = 'Saving...';
                    spinner.classList.remove('d-none');
                    button.disabled = true;
                }
            });

            form.addEventListener('htmx:afterRequest', () => {
                labelSpan.textContent = label;
                spinner.classList.add('d-none');
                button.disabled = false;
            });
        }
    }
}

customElements.define("custom-submit-button", CustomSubmitButton);
