class SmartInput extends HTMLElement {
    connectedCallback() {
        const type = this.getAttribute('type') || 'text';
        const name = this.getAttribute('name') || 'input';
        const label = this.getAttribute('label') || '';
        const required = this.hasAttribute('required');
        const placeholder = this.getAttribute('placeholder') || '';
        const rows = this.getAttribute('rows') || 4;
        const multiple = this.hasAttribute('multiple');
        const options = this.getAttribute('data-options');
        const errorMsg = this.getAttribute('data-error') || `Invalid ${label.toLowerCase()}`;
        const fetchUrl = this.getAttribute('data-url');
        const bindTo = this.getAttribute('data-bind');
        const value = this.getAttribute('value') || '';

        this.innerHTML = `
            <label class="form-label">${label}</label>
            <div class="input-container position-relative"></div>
            <div class="invalid-feedback d-none">${errorMsg}</div>
        `;

        const container = this.querySelector('.input-container');
        const error = this.querySelector('.invalid-feedback');

        let input;

        if (type === 'textarea') {
            input = document.createElement('textarea');
            input.name = name;
            input.className = 'form-control';
            input.rows = rows;
            if (placeholder) input.placeholder = placeholder;
            input.value = value;
        }

        else if (type === 'select') {
            input = document.createElement('select');
            input.name = name;
            input.className = 'form-select';
            if (multiple) input.multiple = true;

            if (options) {
                try {
                    const opts = JSON.parse(options);
                    this.renderOptions(input, opts);
                } catch (e) {
                    console.warn('Invalid JSON in data-options:', options);
                }
            }

            if (fetchUrl) {
                this.createSearchBox(container, input, fetchUrl);
            }

            input.value = value;
        }

        else {
            input = document.createElement('input');
            input.type = type;
            input.name = name;
            input.className = 'form-control';
            if (placeholder) input.placeholder = placeholder;
            input.value = value;
        }

        if (required) input.required = true;
        container.appendChild(input);

        // Validation
        input.addEventListener('blur', () => {
            if (!input.checkValidity()) {
                error.classList.remove('d-none');
                input.classList.add('is-invalid');
                this.classList.add('shake');
                setTimeout(() => this.classList.remove('shake'), 500);
            } else {
                error.classList.add('d-none');
                input.classList.remove('is-invalid');
            }
        });

        // Inject styles for shake and loading
        const style = document.createElement('style');
        style.textContent = `
            .shake {
                animation: shake 0.3s ease-in-out;
            }
            @keyframes shake {
                0%, 100% { transform: translateX(0); }
                25% { transform: translateX(-5px); }
                50% { transform: translateX(5px); }
                75% { transform: translateX(-5px); }
            }
            .spinner {
                position: absolute;
                right: 10px;
                top: 8px;
                width: 1rem;
                height: 1rem;
                border: 2px solid #ccc;
                border-top: 2px solid #333;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
                display: none;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        this.appendChild(style);
    }

    renderOptions(select, options) {
        options.forEach(opt => {
            const option = document.createElement('option');
            option.value = opt.id;
            option.textContent = opt.name;
            select.appendChild(option);
        });
    }

    createSearchBox(container, select, url) {
        const inputBox = document.createElement('input');
        inputBox.className = 'form-control mb-1';
        inputBox.placeholder = 'Search...';

        const spinner = document.createElement('div');
        spinner.className = 'spinner';
        container.appendChild(spinner);

        container.insertBefore(inputBox, select);

        inputBox.addEventListener('input', () => {
            const term = inputBox.value.trim();
            if (term.length > 1) {
                spinner.style.display = 'inline-block';
                fetch(`${url}?q=${term}`)
                    .then(res => res.json())
                    .then(data => {
                        select.innerHTML = '';
                        this.renderOptions(select, data);
                        spinner.style.display = 'none';
                    }).catch(err => {
                        console.error(err);
                        spinner.style.display = 'none';
                    });
            }
        });
    }
}

customElements.define('smart-input', SmartInput);

