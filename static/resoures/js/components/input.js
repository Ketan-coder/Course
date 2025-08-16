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

        // Switch-specific attributes
        const isBig = this.hasAttribute('is-big');
        const isMedium = this.hasAttribute('is-medium');
        const isSmall = this.hasAttribute('is-small');
        const selectedValue = this.getAttribute('selected-value') || '';
        const switchId = this.getAttribute('id') || `switch-${Math.random().toString(36).substr(2, 9)}`;

        // Date picker specific attributes
        const minDate = this.getAttribute('min-date') || '';
        const maxDate = this.getAttribute('max-date') || '';
        const dateFormat = this.getAttribute('date-format') || 'dd-mm-yyyy';

        // File upload specific attributes
        const accept = this.getAttribute('accept') || '';
        const maxSize = this.getAttribute('max-size') || ''; // in MB
        const maxFiles = this.getAttribute('max-files') || '1';
        const allowedTypes = this.getAttribute('allowed-types') || ''; // 'images', 'videos', 'documents', etc.

        const onInputFn = this.getAttribute('data-oninput');
        const onClickFn = this.getAttribute('data-onclick');
        const onChangeFn = this.getAttribute('data-onchange');

        this.innerHTML = `
            ${type === 'checkbox' || type === 'radio' || type === 'switch' ? '' : `<label class="form-label">${label}:${required ? '<span class="text-danger"> * </span>' : ''} </label>`}
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
                    // Set the selected value after options are rendered
                    if (value) {
                        input.value = value;
                        // If value still doesn't match, try to find by text content
                        if (input.value !== value) {
                            const optionElements = input.querySelectorAll('option');
                            for (let opt of optionElements) {
                                if (opt.textContent.toLowerCase() === value.toLowerCase() || 
                                    opt.value.toLowerCase() === value.toLowerCase()) {
                                    opt.selected = true;
                                    break;
                                }
                            }
                        }
                    }
                } catch (e) {
                    console.warn('Invalid JSON in data-options:', options);
                }
            }

            if (fetchUrl) this.createSearchBox(container, input, fetchUrl);

            container.appendChild(input);
        }

        else if (type === 'datepicker') {
            // Create hidden input for form submission (dd-mm-yyyy format)
            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = name;
            hiddenInput.value = value;

            // Create display input for user interaction
            input = document.createElement('input');
            input.type = 'text';
            input.className = 'form-control';
            input.placeholder = placeholder || 'Select date...';
            input.readonly = true;
            input.style.cursor = 'pointer';

            // Create actual date input (hidden)
            const dateInput = document.createElement('input');
            dateInput.type = 'date';
            dateInput.style.position = 'absolute';
            dateInput.style.opacity = '0';
            dateInput.style.pointerEvents = 'none';

            if (minDate) {
                const minDateISO = this.convertDDMMYYYYToISO(minDate);
                if (minDateISO) dateInput.min = minDateISO;
            }
            if (maxDate) {
                const maxDateISO = this.convertDDMMYYYYToISO(maxDate);
                if (maxDateISO) dateInput.max = maxDateISO;
            }

            // Set initial values if provided
            if (value) {
                const isoDate = this.convertDDMMYYYYToISO(value);
                if (isoDate) {
                    dateInput.value = isoDate;
                    input.value = this.formatDateForDisplay(new Date(isoDate));
                    hiddenInput.value = value;
                }
            }

            // Add calendar icon
            const calendarIcon = document.createElement('i');
            calendarIcon.className = 'ph ph-calendar';
            calendarIcon.style.position = 'absolute';
            calendarIcon.style.right = '10px';
            calendarIcon.style.top = '50%';
            calendarIcon.style.transform = 'translateY(-50%)';
            calendarIcon.style.pointerEvents = 'none';
            calendarIcon.style.color = '#6c757d';

            // Handle clicks on display input and icon
            input.addEventListener('click', () => {
                dateInput.showPicker();
            });

            // Handle date selection
            dateInput.addEventListener('change', () => {
                if (dateInput.value) {
                    const selectedDate = new Date(dateInput.value);
                    input.value = this.formatDateForDisplay(selectedDate);
                    hiddenInput.value = this.formatDateDDMMYYYY(selectedDate);
                    
                    // Clear any validation errors
                    error.classList.add('d-none');
                    input.classList.remove('is-invalid');
                    
                    // Trigger change event on hidden input for form handling
                    hiddenInput.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });

            container.appendChild(hiddenInput);
            container.appendChild(input);
            container.appendChild(dateInput);
            container.appendChild(calendarIcon);

            // Store reference to both inputs
            this.inputElement = input;
            this.hiddenInput = hiddenInput;
            this.dateInput = dateInput;

            // Handle required attribute for datepicker
            if (required) {
                hiddenInput.required = true;
                // Add custom validation to display input
                input.addEventListener('blur', () => {
                    if (required && !hiddenInput.value) {
                        error.textContent = 'Date is required';
                        error.classList.remove('d-none');
                        input.classList.add('is-invalid');
                        input.classList.add('shake');
                        setTimeout(() => input.classList.remove('shake'), 400);
                    } else {
                        error.classList.add('d-none');
                        input.classList.remove('is-invalid');
                    }
                });
            }
        }

        else if (type === 'file') {
            input = document.createElement('input');
            input.type = 'file';
            input.name = name;
            input.className = 'form-control';
            
            // Set file attributes
            if (parseInt(maxFiles) > 1) {
                input.multiple = true;
            }
            
            // Set accept attribute based on allowed-types or custom accept
            const acceptAttr = this.getFileAcceptAttribute(allowedTypes, accept);
            if (acceptAttr) {
                input.accept = acceptAttr;
            }

            // Create file info display
            const fileInfo = document.createElement('div');
            fileInfo.className = 'file-info mt-2 d-none';
            fileInfo.innerHTML = `
                <div class="selected-files"></div>
                <small class="text-muted file-constraints"></small>
            `;

            // Set up file constraints display
            this.updateFileConstraintsDisplay(fileInfo.querySelector('.file-constraints'), allowedTypes, maxSize, maxFiles);

            container.appendChild(input);
            container.appendChild(fileInfo);

            // Store references
            this.inputElement = input;
            this.fileInfo = fileInfo;

            // Handle file selection
            input.addEventListener('change', (e) => {
                const files = Array.from(e.target.files);
                const validation = this.validateFiles(files, allowedTypes, maxSize, maxFiles);
                
                if (validation.isValid) {
                    this.displaySelectedFiles(files, fileInfo.querySelector('.selected-files'));
                    fileInfo.classList.remove('d-none');
                    error.classList.add('d-none');
                    input.classList.remove('is-invalid');
                } else {
                    error.textContent = validation.message;
                    error.classList.remove('d-none');
                    input.classList.add('is-invalid');
                    input.classList.add('shake');
                    setTimeout(() => input.classList.remove('shake'), 400);
                    input.value = ''; // Clear invalid selection
                    fileInfo.classList.add('d-none');
                }
            });
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

        else if (type === 'switch') {
            input = document.createElement('input');
            input.type = 'checkbox';
            input.name = name;
            input.id = switchId;
            input.setAttribute('role', 'switch');
            input.value = selectedValue;
            
            // Set checked state based on value or selected-value
            input.checked = value === 'true' || value === '1' || selectedValue === 'true' || selectedValue === '1';
            
            // Build class names for switch input
            let inputClasses = ['form-check-input'];
            if (isBig) inputClasses.push('form-check-input-lg');
            else if (isSmall) inputClasses.push('form-check-input-sm');
            // Medium is default, no additional class needed
            
            input.className = inputClasses.join(' ');

            const labelEl = document.createElement('label');
            labelEl.className = 'form-check-label';
            labelEl.setAttribute('for', switchId);
            labelEl.textContent = label;
            labelEl.style.marginLeft = '10px';
            if (required) input.required = true;
            if (isBig) labelEl.style.fontSize = '1.25rem';
            if (isMedium) labelEl.style.fontSize = '1rem';
            if (isSmall) labelEl.style.fontSize = '0.875rem';

            const wrapper = document.createElement('div');
            let wrapperClasses = ['form-check', 'form-switch'];
            if (isBig) wrapperClasses.push('form-switch-lg');
            else if (isSmall) wrapperClasses.push('form-switch-sm');
            
            wrapper.className = wrapperClasses.join(' ');
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

        if (input && type !== 'datepicker' && type !== 'file') {
            if (required) input.required = true;
            this.attachEvents(input, error, onInputFn, onClickFn, onChangeFn);
        } else if (type === 'file' && input) {
            if (required) input.required = true;
            // File inputs handle their own validation in the change event
            // But still attach other events
            input.addEventListener('click', e => {
                if (onClickFn && window[onClickFn]) window[onClickFn](e);
            });
        }

        // Store reference to the main input for easy access
        if (type !== 'datepicker') {
            this.inputElement = input;
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
            
            /* Additional switch size styling if needed */
            .form-switch-lg .form-check-input-lg {
                width: 3em;
                height: 1.75em;
            }
            .form-switch-sm .form-check-input-sm {
                width: 1.75em;
                height: 1em;
            }
            
            /* Date picker styling */
            .input-container {
                position: relative;
            }
            
            /* File upload styling */
            .file-info {
                border: 1px solid #dee2e6;
                border-radius: 0.375rem;
                padding: 0.75rem;
                background-color: #f8f9fa;
            }
            .selected-files {
                margin-bottom: 0.5rem;
            }
            .file-item {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0.25rem 0;
                border-bottom: 1px solid #dee2e6;
            }
            .file-item:last-child {
                border-bottom: none;
            }
            .file-details {
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            .file-icon {
                font-size: 1.2rem;
                color: #6c757d;
            }
            .file-name {
                font-weight: 500;
            }
            .file-size {
                color: #6c757d;
                font-size: 0.875rem;
            }
            .remove-file {
                background: none;
                border: none;
                color: #dc3545;
                cursor: pointer;
                padding: 0.25rem;
                border-radius: 0.25rem;
            }
            .remove-file:hover {
                background-color: #f5c6cb;
            }
        `;
        this.appendChild(style);
    }

    // Date utility methods
    convertDDMMYYYYToISO(dateStr) {
        if (!dateStr) return null;
        const parts = dateStr.split('-');
        if (parts.length !== 3) return null;
        
        const day = parts[0].padStart(2, '0');
        const month = parts[1].padStart(2, '0');
        const year = parts[2];
        
        // Validate date parts
        if (year.length !== 4 || isNaN(day) || isNaN(month) || isNaN(year)) return null;
        if (parseInt(month) < 1 || parseInt(month) > 12) return null;
        if (parseInt(day) < 1 || parseInt(day) > 31) return null;
        
        return `${year}-${month}-${day}`;
    }

    formatDateForDisplay(date) {
        const options = { 
            day: '2-digit', 
            month: 'long', 
            year: 'numeric' 
        };
        return date.toLocaleDateString('en-GB', options);
    }

    formatDateDDMMYYYY(date) {
        const day = date.getDate().toString().padStart(2, '0');
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const year = date.getFullYear();
        return `${day}-${month}-${year}`;
    }

    validateDate(dateStr) {
        if (!dateStr) return false;
        
        const isoDate = this.convertDDMMYYYYToISO(dateStr);
        if (!isoDate) return false;
        
        const date = new Date(isoDate);
        return date instanceof Date && !isNaN(date);
    }

    // File utility methods
    getFileAcceptAttribute(allowedTypes, customAccept) {
        if (customAccept) return customAccept;
        
        const typeMap = {
            'images': 'image/*',
            'videos': 'video/*',
            'documents': '.pdf,.doc,.docx,.txt,.rtf',
            'spreadsheets': '.xls,.xlsx,.csv',
            'presentations': '.ppt,.pptx',
            'archives': '.zip,.rar,.7z,.tar,.gz',
            'audio': 'audio/*'
        };
        
        return typeMap[allowedTypes] || '';
    }

    validateFiles(files, allowedTypes, maxSize, maxFiles) {
        const maxFilesNum = parseInt(maxFiles) || 1;
        const maxSizeMB = parseFloat(maxSize) || null;
        
        // Check number of files
        if (files.length > maxFilesNum) {
            return {
                isValid: false,
                message: `Maximum ${maxFilesNum} file(s) allowed`
            };
        }
        
        // Check each file
        for (let file of files) {
            // Check file size
            if (maxSizeMB && file.size > maxSizeMB * 1024 * 1024) {
                return {
                    isValid: false,
                    message: `File "${file.name}" exceeds maximum size of ${maxSizeMB}MB`
                };
            }
            
            // Check file type
            if (allowedTypes && !this.isFileTypeAllowed(file, allowedTypes)) {
                return {
                    isValid: false,
                    message: `File type not allowed for "${file.name}". Only ${allowedTypes} are allowed.`
                };
            }
        }
        
        return { isValid: true, message: '' };
    }

    isFileTypeAllowed(file, allowedTypes) {
        const typeChecks = {
            'images': file.type.startsWith('image/'),
            'videos': file.type.startsWith('video/'),
            'documents': [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'text/plain',
                'application/rtf'
            ].includes(file.type),
            'spreadsheets': [
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'text/csv'
            ].includes(file.type),
            'presentations': [
                'application/vnd.ms-powerpoint',
                'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            ].includes(file.type),
            'archives': [
                'application/zip',
                'application/x-rar-compressed',
                'application/x-7z-compressed',
                'application/x-tar',
                'application/gzip'
            ].includes(file.type),
            'audio': file.type.startsWith('audio/')
        };
        
        return typeChecks[allowedTypes] || true;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    getFileIcon(file) {
        if (file.type.startsWith('image/')) return 'ph ph-image';
        if (file.type.startsWith('video/')) return 'ph ph-video';
        if (file.type.startsWith('audio/')) return 'ph ph-music-note';
        if (file.type === 'application/pdf') return 'ph ph-file-pdf';
        if (file.type.includes('word') || file.type.includes('document')) return 'ph ph-file-doc';
        if (file.type.includes('sheet') || file.type.includes('excel')) return 'ph ph-file-xls';
        if (file.type.includes('presentation') || file.type.includes('powerpoint')) return 'ph ph-file-ppt';
        if (file.type.includes('zip') || file.type.includes('rar') || file.type.includes('archive')) return 'ph ph-file-zip';
        return 'ph ph-file';
    }

    displaySelectedFiles(files, container) {
        container.innerHTML = '';
        
        files.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            
            fileItem.innerHTML = `
                <div class="file-details">
                    <i class="${this.getFileIcon(file)} file-icon"></i>
                    <div>
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${this.formatFileSize(file.size)}</div>
                    </div>
                </div>
                <button type="button" class="remove-file" data-index="${index}">
                    <i class="ph ph-x"></i>
                </button>
            `;
            
            // Handle file removal
            const removeBtn = fileItem.querySelector('.remove-file');
            removeBtn.addEventListener('click', () => {
                this.removeFile(index);
            });
            
            container.appendChild(fileItem);
        });
    }

    removeFile(index) {
        if (!this.inputElement) return;
        
        const dt = new DataTransfer();
        const files = Array.from(this.inputElement.files);
        
        files.forEach((file, i) => {
            if (i !== index) {
                dt.items.add(file);
            }
        });
        
        this.inputElement.files = dt.files;
        
        // Update display
        if (dt.files.length > 0) {
            this.displaySelectedFiles(Array.from(dt.files), this.fileInfo.querySelector('.selected-files'));
        } else {
            this.fileInfo.classList.add('d-none');
        }
    }

    updateFileConstraintsDisplay(container, allowedTypes, maxSize, maxFiles) {
        const constraints = [];
        
        if (allowedTypes) {
            constraints.push(`Types: ${allowedTypes}`);
        }
        if (maxSize) {
            constraints.push(`Max size: ${maxSize}MB`);
        }
        if (parseInt(maxFiles) > 1) {
            constraints.push(`Max files: ${maxFiles}`);
        }
        
        if (constraints.length > 0) {
            container.textContent = constraints.join(' • ');
        }
    }

    // Add getter and setter for value property
    get value() {
        const type = this.getAttribute('type') || 'text';
        if (type === 'datepicker') {
            return this.hiddenInput ? this.hiddenInput.value : '';
        } else if (type === 'file') {
            return this.inputElement ? this.inputElement.files : null;
        } else if (type === 'checkbox' || type === 'switch') {
            return this.inputElement ? this.inputElement.checked : false;
        } else if (type === 'radio') {
            const radios = this.querySelectorAll('input[type="radio"]');
            for (let radio of radios) {
                if (radio.checked) return radio.value;
            }
            return '';
        }
        return this.inputElement ? this.inputElement.value : '';
    }

    set value(val) {
        const type = this.getAttribute('type') || 'text';
        if (type === 'datepicker') {
            if (this.hiddenInput && this.inputElement && this.dateInput) {
                if (val && this.validateDate(val)) {
                    const isoDate = this.convertDDMMYYYYToISO(val);
                    if (isoDate) {
                        this.dateInput.value = isoDate;
                        this.inputElement.value = this.formatDateForDisplay(new Date(isoDate));
                        this.hiddenInput.value = val;
                    }
                } else {
                    this.dateInput.value = '';
                    this.inputElement.value = '';
                    this.hiddenInput.value = '';
                }
            }
        } else if (type === 'file') {
            // File inputs cannot be set programmatically for security reasons
            console.warn('File input values cannot be set programmatically');
        } else if (type === 'checkbox' || type === 'switch') {
            if (this.inputElement) {
                this.inputElement.checked = val === 'true' || val === '1' || val === true;
            }
        } else if (type === 'radio') {
            const radios = this.querySelectorAll('input[type="radio"]');
            radios.forEach(radio => {
                radio.checked = radio.value == val;
            });
        } else if (type === 'select') {
            if (this.inputElement) {
                this.inputElement.value = val;
                // If value still doesn't match, try to find by text content
                if (this.inputElement.value !== val) {
                    const optionElements = this.inputElement.querySelectorAll('option');
                    for (let opt of optionElements) {
                        if (opt.textContent.toLowerCase() === val.toLowerCase() || 
                            opt.value.toLowerCase() === val.toLowerCase()) {
                            opt.selected = true;
                            break;
                        }
                    }
                }
            }
        } else if (this.inputElement) {
            this.inputElement.value = val;
        }
        // Update the attribute directly without triggering setAttribute override
        if (type !== 'file') {
            super.setAttribute('value', val);
        }
    }

    // Override setAttribute to handle value updates
    setAttribute(name, value) {
        super.setAttribute(name, value);
        if (name === 'value' && (this.inputElement || this.hiddenInput)) {
            // Update the actual input value when value attribute changes
            // Call the internal update method to avoid circular calls
            this._updateInputValue(value);
        }
    }

    // Internal method to update input value without triggering attribute update
    _updateInputValue(val) {
        const type = this.getAttribute('type') || 'text';
        if (type === 'datepicker') {
            if (this.hiddenInput && this.inputElement && this.dateInput) {
                if (val && this.validateDate(val)) {
                    const isoDate = this.convertDDMMYYYYToISO(val);
                    if (isoDate) {
                        this.dateInput.value = isoDate;
                        this.inputElement.value = this.formatDateForDisplay(new Date(isoDate));
                        this.hiddenInput.value = val;
                    }
                }
            }
        } else if (type === 'checkbox' || type === 'switch') {
            if (this.inputElement) {
                this.inputElement.checked = val === 'true' || val === '1' || val === true;
            }
        } else if (type === 'radio') {
            const radios = this.querySelectorAll('input[type="radio"]');
            radios.forEach(radio => {
                radio.checked = radio.value == val;
            });
        } else if (type === 'select') {
            if (this.inputElement) {
                this.inputElement.value = val;
                // If value still doesn't match, try to find by text content
                if (this.inputElement.value !== val) {
                    const optionElements = this.inputElement.querySelectorAll('option');
                    for (let opt of optionElements) {
                        if (opt.textContent.toLowerCase() === val.toLowerCase() || 
                            opt.value.toLowerCase() === val.toLowerCase()) {
                            opt.selected = true;
                            break;
                        }
                    }
                }
            }
        } else if (this.inputElement) {
            this.inputElement.value = val;
        }
    }

    // Method to get the actual input element
    getInputElement() {
        return this.inputElement;
    }

    // Method to get the hidden input for datepicker
    getHiddenInput() {
        return this.hiddenInput;
    }

    // Method to focus the input
    focus() {
        if (this.inputElement) {
            this.inputElement.focus();
        }
    }

    // Method to validate the input
    validate() {
        const type = this.getAttribute('type') || 'text';
        const error = this.querySelector('.invalid-feedback');
        const required = this.hasAttribute('required');
        
        if (type === 'datepicker') {
            const value = this.hiddenInput ? this.hiddenInput.value : '';
            
            if (required && !value) {
                error.textContent = 'Date is required';
                error.classList.remove('d-none');
                this.inputElement.classList.add('is-invalid');
                this.inputElement.classList.add('shake');
                setTimeout(() => this.inputElement.classList.remove('shake'), 400);
                return false;
            } else if (value && !this.validateDate(value)) {
                error.textContent = 'Invalid date format (dd-mm-yyyy)';
                error.classList.remove('d-none');
                this.inputElement.classList.add('is-invalid');
                this.inputElement.classList.add('shake');
                setTimeout(() => this.inputElement.classList.remove('shake'), 400);
                return false;
            } else {
                error.classList.add('d-none');
                this.inputElement.classList.remove('is-invalid');
                return true;
            }
        } else if (type === 'file') {
            const files = this.inputElement ? Array.from(this.inputElement.files) : [];
            
            if (required && files.length === 0) {
                error.textContent = 'File is required';
                error.classList.remove('d-none');
                this.inputElement.classList.add('is-invalid');
                this.inputElement.classList.add('shake');
                setTimeout(() => this.inputElement.classList.remove('shake'), 400);
                return false;
            } else if (files.length > 0) {
                const allowedTypes = this.getAttribute('allowed-types') || '';
                const maxSize = this.getAttribute('max-size') || '';
                const maxFiles = this.getAttribute('max-files') || '1';
                
                const validation = this.validateFiles(files, allowedTypes, maxSize, maxFiles);
                if (!validation.isValid) {
                    error.textContent = validation.message;
                    error.classList.remove('d-none');
                    this.inputElement.classList.add('is-invalid');
                    this.inputElement.classList.add('shake');
                    setTimeout(() => this.inputElement.classList.remove('shake'), 400);
                    return false;
                }
            }
            
            error.classList.add('d-none');
            this.inputElement.classList.remove('is-invalid');
            return true;
        } else if (this.inputElement) {
            if (!this.inputElement.checkValidity()) {
                error.classList.remove('d-none');
                this.inputElement.classList.add('is-invalid');
                this.inputElement.classList.add('shake');
                setTimeout(() => this.inputElement.classList.remove('shake'), 400);
                return false;
            } else {
                error.classList.add('d-none');
                this.inputElement.classList.remove('is-invalid');
                return true;
            }
        }
        return true;
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