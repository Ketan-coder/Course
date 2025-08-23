class SmartQuill extends HTMLElement {
    constructor() {
        super();
        this.editor = null;
    }

    static get observedAttributes() {
        return ['value'];
    }

    get value() {
        return this.editor ? this.editor.root.innerHTML : '';
    }

    set value(newValue) {
        if (this.editor && newValue !== this.editor.root.innerHTML) {
            this.editor.root.innerHTML = newValue;
            const hiddenInput = this.querySelector(`input[name="${this.getAttribute('name') || 'richtext'}"]`);
            if (hiddenInput) {
                hiddenInput.value = newValue;
            }
        }
    }

    connectedCallback() {
        const name = this.getAttribute('name') || 'richtext';
        const label = this.getAttribute('label') || 'Description';
        const placeholder = this.getAttribute('placeholder') || '';
        const required = this.hasAttribute('required');
        const requiredMessage = this.getAttribute('required-message') || `${label} is required`;

        const content = this.getAttribute('value') || this.textContent.trim();

        this.innerHTML = `
            <div class="smart-quill-container">
                <label class="form-label smart-quill-label">
                    ${label}${required ? '<span class="text-danger"> *</span>' : ''}
                </label>
                <div class="quill-container">
                    <div class="quill-editor" style="min-height: 200px;"></div>
                    <input type="hidden" name="${name}" />
                </div>
                <div class="invalid-feedback d-none">${requiredMessage}</div>
            </div>
        `;

        // Store config
        this.config = {
            name, label, placeholder, required, requiredMessage
        };

        const editorContainer = this.querySelector('.quill-editor');
        const hiddenInput = this.querySelector(`input[name="${name}"]`);
        this.errorFeedback = this.querySelector('.invalid-feedback');
        this.container = this.querySelector('.smart-quill-container');
        this.quillContainer = this.querySelector('.quill-container');

        // Load Quill CSS if not already loaded
        this.loadQuillStyles();

        // Initialize Quill editor
        this.editor = new Quill(editorContainer, {
            theme: 'snow',
            placeholder: placeholder,
            modules: {
                toolbar: [
                    ['bold', 'italic', 'underline', 'strike'],
                    ['blockquote', 'code-block'],
                    ['link', 'image', 'video', 'formula'],
                    [{ 'header': 1 }, { 'header': 2 }],
                    [{ 'list': 'ordered'}, { 'list': 'bullet' }, { 'list': 'check' }],
                    [{ 'script': 'sub'}, { 'script': 'super' }],
                    [{ 'indent': '-1'}, { 'indent': '+1' }],
                    [{ 'direction': 'rtl' }],
                    [{ 'size': ['small', false, 'large', 'huge'] }],
                    [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
                    [{ 'color': [] }, { 'background': [] }],
                    [{ 'font': [] }],
                    [{ 'align': [] }],
                    ['code-block'],
                    ['clean']
                ],
                history: {
                    delay: 1000,
                    maxStack: 500,
                    userOnly: true
                }
            }
        });

        if (content) {
            this.editor.root.innerHTML = content;
            hiddenInput.value = content;
        }

        // Handle text changes
        this.editor.on('text-change', () => {
            const htmlContent = this.editor.root.innerHTML;
            hiddenInput.value = htmlContent;
            
            // Hide validation error when user starts typing
            if (this.hasContent()) {
                this.hideValidationError();
            }
            
            this.dispatchEvent(new CustomEvent('input', { 
                bubbles: true,
                detail: { value: htmlContent }
            }));
        });

        // Handle focus/blur for validation
        this.editor.on('selection-change', (range, oldRange, source) => {
            if (range === null && this.config.required) {
                // Editor lost focus, validate if required
                setTimeout(() => this.validate(), 100);
            }
        });

        // Add custom styles
        // this.addStyles();
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (name === 'value' && this.editor) {
            this.value = newValue;
        }
    }

    // Check if editor has meaningful content
    hasContent() {
        if (!this.editor) return false;
        
        const text = this.editor.getText().trim();
        const html = this.editor.root.innerHTML;
        
        // Check if there's actual text content (not just empty paragraphs or whitespace)
        return text.length > 0 && html !== '<p><br></p>' && html !== '<p></p>';
    }

    // Validation method
    validate() {
        if (!this.config.required) {
            return true;
        }

        const isValid = this.hasContent();
        
        if (!isValid) {
            this.showValidationError();
        } else {
            this.hideValidationError();
        }
        
        return isValid;
    }

    showValidationError() {
        if (this.quillContainer && this.errorFeedback && this.container) {
            this.quillContainer.classList.add('is-invalid');
            this.errorFeedback.classList.remove('d-none');
            this.container.classList.add('shake');
            
            // Remove shake animation after it completes
            setTimeout(() => {
                this.container.classList.remove('shake');
            }, 500);
        }
    }

    hideValidationError() {
        if (this.quillContainer && this.errorFeedback) {
            this.quillContainer.classList.remove('is-invalid');
            this.errorFeedback.classList.add('d-none');
        }
    }

    // Form integration methods
    checkValidity() {
        return this.validate();
    }

    reportValidity() {
        const isValid = this.validate();
        if (!isValid && this.editor) {
            this.editor.focus();
        }
        return isValid;
    }

    // Public methods
    focus() {
        if (this.editor) {
            this.editor.focus();
        }
    }

    blur() {
        if (this.editor) {
            this.editor.blur();
        }
    }

    clear() {
        if (this.editor) {
            this.editor.setText('');
            this.hideValidationError();
        }
    }

    getLength() {
        return this.editor ? this.editor.getLength() : 0;
    }

    getText() {
        return this.editor ? this.editor.getText() : '';
    }

    getHTML() {
        return this.editor ? this.editor.root.innerHTML : '';
    }

    loadQuillStyles() {
        // Load Quill CSS if not already loaded
        if (!document.querySelector('link[href*="quill"]')) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'https://cdnjs.cloudflare.com/ajax/libs/quill/1.3.7/quill.snow.min.css';
            document.head.appendChild(link);
        }

        // Load Quill JS if not already loaded
        if (typeof Quill === 'undefined') {
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/quill/1.3.7/quill.min.js';
            script.onload = () => {
                // Re-initialize if Quill was loaded after component creation
                if (!this.editor) {
                    this.connectedCallback();
                }
            };
            document.head.appendChild(script);
        }
    }

    // addStyles() {
    //     const style = document.createElement('style');
    //     style.textContent = `
    //         .smart-quill-container {
    //             position: relative;
    //         }

    //         .smart-quill-label {
    //             font-weight: 500;
    //             margin-bottom: 0.5rem;
    //             color: #374151;
    //         }

    //         .quill-container {
    //             position: relative;
    //         }

    //         .quill-container.is-invalid .ql-container {
    //             border-color: #dc3545 !important;
    //             box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25) !important;
    //         }

    //         .quill-container.is-invalid .ql-toolbar {
    //             border-color: #dc3545 !important;
    //         }

    //         /* Validation styles */
    //         .invalid-feedback {
    //             display: none;
    //             width: 100%;
    //             margin-top: 0.25rem;
    //             font-size: 0.875rem;
    //             color: #dc3545;
    //         }

    //         .invalid-feedback:not(.d-none) {
    //             display: block;
    //         }

    //         /* Shake animation */
    //         .shake {
    //             animation: shake 0.5s ease-in-out;
    //         }

    //         @keyframes shake {
    //             0%, 100% { transform: translateX(0); }
    //             10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
    //             20%, 40%, 60%, 80% { transform: translateX(5px); }
    //         }

    //         /* Enhanced Quill styling */
    //         .ql-container {
    //             font-size: 14px;
    //             border-bottom-left-radius: 0.375rem;
    //             border-bottom-right-radius: 0.375rem;
    //         }

    //         .ql-toolbar {
    //             border-top-left-radius: 0.375rem;
    //             border-top-right-radius: 0.375rem;
    //             background: #f8f9fa;
    //         }

    //         .ql-editor {
    //             min-height: 150px;
    //             max-height: 400px;
    //             overflow-y: auto;
    //         }

    //         .ql-editor.ql-blank::before {
    //             font-style: italic;
    //             color: #6b7280;
    //         }

    //         /* Dark mode support */
    //         @media (prefers-color-scheme: dark) {
    //             .smart-quill-label {
    //                 color: #f3f4f6;
    //             }

    //             .ql-toolbar {
    //                 background: #374151;
    //                 border-color: #4b5563;
    //             }

    //             .ql-container {
    //                 border-color: #4b5563;
    //                 background: #1f2937;
    //             }

    //             .ql-editor {
    //                 color: #f3f4f6;
    //             }

    //             .ql-editor.ql-blank::before {
    //                 color: #9ca3af;
    //             }
    //         }

    //         /* Utility classes */
    //         .d-none {
    //             display: none !important;
    //         }

    //         .text-danger {
    //             color: #dc3545 !important;
    //         }
    //     `;
    //     this.appendChild(style);
    // }
}

customElements.define('smart-quill', SmartQuill);