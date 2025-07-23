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
        const content = this.getAttribute('value') || this.textContent.trim();

        this.innerHTML = `
            <label class="form-label">${label}</label>
            <div class="quill-container">
                <div class="quill-editor" style="min-height: 200px;"></div>
                <input type="hidden" name="${name}" />
            </div>
        `;

        const editorContainer = this.querySelector('.quill-editor');
        const hiddenInput = this.querySelector(`input[name="${name}"]`);

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

        this.editor.on('text-change', () => {
            hiddenInput.value = this.editor.root.innerHTML;
            this.dispatchEvent(new CustomEvent('input', { 
                bubbles: true,
                detail: { value: this.value }
            }));
        });
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (name === 'value' && this.editor) {
            this.value = newValue;
        }
    }
}

customElements.define('smart-quill', SmartQuill);