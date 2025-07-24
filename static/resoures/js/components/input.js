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
        const value = this.getAttribute('value') || '';

        const onInputFn = this.getAttribute('data-oninput');
        const onClickFn = this.getAttribute('data-onclick');
        const onChangeFn = this.getAttribute('data-onchange');

        this.innerHTML = `
            ${type === 'checkbox' || type === 'radio' ? '' : `<label class="form-label">${label}:${required ? '<span class="text-danger"> * </span>' : ''} </label>`}
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
            input.placeholder = placeholder;
            input.value = value;
            container.appendChild(input);
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

            if (fetchUrl) this.createSearchBox(container, input, fetchUrl);

            input.value = value;
            container.appendChild(input);
        }

        else if (type === 'checkbox') {
            input = document.createElement('input');
            input.type = 'checkbox';
            input.name = name;
            input.checked = value === 'true' || value === '1';
            input.className = 'form-check-input me-2';

            const labelEl = document.createElement('label');
            labelEl.className = 'form-check-label';
            labelEl.textContent = label;

            const wrapper = document.createElement('div');
            wrapper.className = 'form-check';
            wrapper.appendChild(input);
            wrapper.appendChild(labelEl);
            container.appendChild(wrapper);
        }

        else if (type === 'radio') {
            if (!options) return;
            try {
                const opts = JSON.parse(options);
                opts.forEach(opt => {
                    const radio = document.createElement('input');
                    radio.type = 'radio';
                    radio.name = name;
                    radio.value = opt.id;
                    radio.className = 'form-check-input me-2';
                    if (opt.id == value) radio.checked = true;

                    const labelEl = document.createElement('label');
                    labelEl.className = 'form-check-label me-3';
                    labelEl.textContent = opt.name;

                    const wrapper = document.createElement('div');
                    wrapper.className = 'form-check form-check-inline';
                    wrapper.appendChild(radio);
                    wrapper.appendChild(labelEl);
                    container.appendChild(wrapper);

                    this.attachEvents(radio, error, onInputFn, onClickFn, onChangeFn);
                });
            } catch (e) {
                console.warn('Invalid JSON in data-options:', options);
            }
            return;
        }

        else {
            input = document.createElement('input');
            input.type = type;
            input.name = name;
            input.className = 'form-control';
            input.placeholder = placeholder;
            input.value = value;
            container.appendChild(input);
        }

        if (input) {
            if (required) input.required = true;
            this.attachEvents(input, error, onInputFn, onClickFn, onChangeFn);
        }

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

    attachEvents(input, error, onInputFn, onClickFn, onChangeFn) {
        // Validation
        input.addEventListener('blur', () => {
            if (!input.checkValidity()) {
                error.classList.remove('d-none');
                input.classList.add('is-invalid');
                input.classList.add('shake');
                setTimeout(() => input.classList.remove('shake'), 400);
            } else {
                error.classList.add('d-none');
                input.classList.remove('is-invalid');
            }
        });

        // Native + Custom Event Hooks
        input.addEventListener('input', e => {
            error.classList.add('d-none');
            input.classList.remove('is-invalid');
            if (onInputFn && window[onInputFn]) window[onInputFn](e);
        });

        input.addEventListener('click', e => {
            if (onClickFn && window[onClickFn]) window[onClickFn](e);
        });

        input.addEventListener('change', e => {
            if (onChangeFn && window[onChangeFn]) window[onChangeFn](e);
        });
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
