
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
                    ['bold', 'italic', 'underline', 'strike'],        // toggled buttons
                    ['blockquote', 'code-block'],
                    ['link', 'image', 'video', 'formula'],
                  
                    [{ 'header': 1 }, { 'header': 2 }],               // custom button values
                    [{ 'list': 'ordered'}, { 'list': 'bullet' }, { 'list': 'check' }],
                    [{ 'script': 'sub'}, { 'script': 'super' }],      // superscript/subscript
                    [{ 'indent': '-1'}, { 'indent': '+1' }],          // outdent/indent
                    [{ 'direction': 'rtl' }],                         // text direction
                  
                    [{ 'size': ['small', false, 'large', 'huge'] }],  // custom dropdown
                    [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
                  
                    [{ 'color': [] }, { 'background': [] }],          // dropdown with defaults from theme
                    [{ 'font': [] }],
                    [{ 'align': [] }],
                    ['code-block'],
                  
                    ['clean']                                         // remove formatting button
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
        }

        this.editor.on('text-change', () => {
            hiddenInput.value = this.editor.root.innerHTML;
        });
    }
}

customElements.define('smart-quill', SmartQuill);
