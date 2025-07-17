class SmartCounter extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: "open" });

        this._value = parseInt(this.getAttribute("value") || 0);
        this._label = this.getAttribute("label") || "Points";
        this.shadowRoot.innerHTML = `
            <style>
                .counter {
                    font-weight: bold;
                    font-size: 1.3rem;
                    position: relative;
                    display: inline-block;
                }
                .bounce {
                    animation: bounce 0.4s ease;
                }
                @keyframes bounce {
                    0%   { transform: scale(1); }
                    30%  { transform: scale(1.3); }
                    60%  { transform: scale(0.9); }
                    100% { transform: scale(1); }
                }
                .label {
                    font-size: 0.75rem;
                    color: gray;
                    display: block;
                }
            </style>
            <div class="counter" id="counter">
                <span id="value">${this._value}</span>
                <span class="label">${this._label}</span>
            </div>
        `;
    }

    static get observedAttributes() {
        return ['value'];
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (name === 'value' && oldValue !== newValue) {
            this._value = parseInt(newValue);
            const valEl = this.shadowRoot.getElementById('value');
            valEl.textContent = this._value;
            valEl.classList.remove("bounce");
            void valEl.offsetWidth; // force reflow to restart animation
            valEl.classList.add("bounce");
        }
    }
}
customElements.define('smart-counter', SmartCounter);
