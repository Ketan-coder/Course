class ButtonType {
  static DANGER = 'danger';
  static WARNING = 'warning';
  static SUCCESS = 'success';
  static INFO = 'info';
  static PRIMARY = 'primary';
  static SECONDARY = 'secondary';
}

customElements.define('icon-button', class IconButton extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.isLoading = false;
  }

  connectedCallback() {
    this.setupAttributes();
    this.render();
    this.cacheElements();
    this.bindEvents();
    this.loadStyles();
    this.loadIconLibrary();
  }

  setupAttributes() {
    // Core properties
    this.props = {
      icon: this.getAttribute('icon') || 'circle',
      variant: this.getAttribute('variant') || ButtonType.PRIMARY,
      size: this.getAttribute('size') || 'md',
      text: this.getAttribute('text') || this.getAttribute('label') || '',
      tooltip: this.getAttribute('tooltip') || '',
      rounded: this.getAttribute('rounded') || 'default',
      shadow: this.hasAttribute('shadow'),
      ghost: this.hasAttribute('is_ghost'),
      showSpinner: this.getAttribute('showspinner') === 'true',
      disabled: this.hasAttribute('disabled'),
      loading: this.hasAttribute('loading'),

      // AJAX-related
      formId: this.getAttribute('form-id'),
      postUrl: this.getAttribute('post'),
      method: (this.getAttribute('method') || 'POST').toUpperCase(),
      target: this.getAttribute('target'),
      successMessage: this.getAttribute('success-message'),
      errorMessage: this.getAttribute('error-message'),
      confirmMessage: this.getAttribute('confirm-message'),

      // Callbacks
      onClick: this.getAttribute('data-onclick'),
      onSuccess: this.getAttribute('data-onsuccess'),
      onError: this.getAttribute('data-onerror'),
    };
  }

  render() {
    const p = this.props;
    const variant = p.ghost ? 'ghost' : p.variant;
    const roundedCls = p.rounded !== 'default' ? `icon-btn-${p.rounded}` : '';
    const shadowCls = p.shadow ? 'icon-btn-shadow' : '';
    const spinnerHTML = p.showSpinner
      ? `<span class="spinner-border spinner-border-sm ms-2 d-none" role="status" aria-hidden="true"></span>`
      : '';
    const overlayHTML = p.loading ? `<div class="loading-overlay"></div>` : '';

    this.shadowRoot.innerHTML = `
      <button
        class="icon-btn icon-btn-${variant} icon-btn-${p.size} ${roundedCls} ${shadowCls}"
        role="button"
        ${p.disabled ? 'disabled' : ''}
        ${p.tooltip ? `title="${p.tooltip}"` : ''}
      >
        <i class="ph ph-${p.loading ? 'spinner' : p.icon}" data-weight="${p.loading ? 'bold' : 'regular'}"></i>
        ${p.text ? `<span class="btn-text">${p.text}</span>` : ''}
        ${spinnerHTML}
        ${overlayHTML}
      </button>
    `;
  }

  cacheElements() {
    const root = this.shadowRoot;
    this.btnEl = root.querySelector('button');
    this.iconEl = root.querySelector('i');
    this.textEl = root.querySelector('.btn-text');
    this.spinnerEl = root.querySelector('.spinner-border');
  }

  bindEvents() {
    this.btnEl.addEventListener('click', (e) => this.handleClick(e));
  }

  async handleClick(e) {
    const p = this.props;
    if (p.disabled) e.preventDefault();
    if (p.confirmMessage && !confirm(p.confirmMessage)) return;

    this.rippleEffect(e);

    if (p.postUrl && p.formId) {
      await this.submitFormViaAjax();
    }

    if (p.onClick && typeof window[p.onClick] === 'function') {
      window[p.onClick].call(this, e);
    }
  }

  async submitFormViaAjax() {
    const p = this.props;
    const form = document.getElementById(p.formId);
    if (!form) return this.toToast('Form not found', 'error');

    this.setLoadingState(true);
    try {
      const resp = await fetch(p.postUrl, {
        method: p.method,
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        body: new FormData(form),
      });
      if (!resp.ok) throw new Error(resp.status);

      const text = await resp.text();
      if (p.target) document.querySelector(p.target).innerHTML = text;
      if (p.successMessage) this.toToast(p.successMessage, 'success');
      if (p.onSuccess && typeof window[p.onSuccess] === 'function')
        window[p.onSuccess].call(this, text);
    } catch (err) {
      if (p.errorMessage) this.toToast(p.errorMessage, 'error');
      if (p.onError && typeof window[p.onError] === 'function')
        window[p.onError].call(this, err);
    } finally {
      this.setLoadingState(false);
    }
  }

  setLoadingState(isLoading) {
    this.isLoading = isLoading;
    const { icon, text } = this.props;
    this.btnEl.disabled = isLoading;

    if (isLoading) {
      if (this.textEl) this.textEl.textContent = 'Processing...';
      this.spinnerEl?.classList.remove('d-none');
      this.iconEl.className = 'ph ph-spinner';
      this.iconEl.dataset.weight = 'bold';
    } else {
      if (this.textEl) this.textEl.textContent = text;
      this.spinnerEl?.classList.add('d-none');
      this.iconEl.className = `ph ph-${icon}`;
      this.iconEl.dataset.weight = this.getAttribute('icon-weight') || 'regular';
    }
  }

  rippleEffect(e) {
    const ripple = document.createElement('span');
    const rect = this.btnEl.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    ripple.style.width = ripple.style.height = `${size}px`;
    ripple.style.left = `${e.clientX - rect.left - size / 2}px`;
    ripple.style.top = `${e.clientY - rect.top - size / 2}px`;
    ripple.className = 'ripple';
    this.btnEl.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);
  }

  toToast(msg, type) {
    const t = document.createElement('div');
    t.textContent = msg;
    t.className = `toast-${type}`;
    Object.assign(t.style, {
      position: 'fixed',
      top: '1rem',
      right: '1rem',
      padding: '0.75rem 1rem',
      background: type === 'success' ? '#10b981' : '#ef4444',
      color: '#fff',
      borderRadius: '0.25rem',
      zIndex: 10000,
      opacity: 0,
      transform: 'translateX(100%)',
      transition: 'all .3s'
    });
    document.body.append(t);
    requestAnimationFrame(() => {
      t.style.opacity = '1';
      t.style.transform = 'translateX(0)';
    });
    setTimeout(() => {
      t.style.opacity = '0';
      t.style.transform = 'translateX(100%)';
      setTimeout(() => t.remove(), 300);
    }, 3000);
  }

  loadIconLibrary() {
    if (!document.querySelector('link[href*="phosphor"]')) {
      const l = document.createElement('link');
      l.href = 'https://cdn.jsdelivr.net/npm/phosphor-icons/css/phosphor.css';
      l.rel = 'stylesheet';
      document.head.append(l);
    }
  }

  loadStyles() {
    const css = `
      .icon-btn { /* simplified for brevity… include styles as before… */ }
      .ripple { /* include ripple animation… */ }
      .spinner-border { /* include spinner CSS… */ }
      .toast-success, .toast-error { /* minimal toast styles… */ }
    `;
    const st = document.createElement('style');
    st.textContent = css;
    this.shadowRoot.append(st);
  }
});
