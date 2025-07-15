
class SmartQuill extends HTMLElement {
    constructor() {
        super();
        this.editor = null;
    }

    connectedCallback() {
        const name = this.getAttribute('name') || 'richtext';
        const label = this.getAttribute('label') || 'Description';
        const placeholder = this.getAttribute('placeholder') || '';
        const content = this.textContent.trim();

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
                    [{ header: [1, 2, false] }],
                    ['bold', 'italic', 'underline'],
                    ['link', 'blockquote', 'code-block'],
                    [{ list: 'ordered' }, { list: 'bullet' }]
                ]
            }
        });

        if (content) {
            this.editor.root.innerHTML = content;
        }

        this.editor.on('text-change', () => {
            hiddenInput.value = this.editor.root.innerHTML;
        });
    }
}

customElements.define('smart-quill', SmartQuill);
