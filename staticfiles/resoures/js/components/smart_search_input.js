class SmartSearchInput extends HTMLElement {
    constructor() {
        super();
        this.selectedItems = new Map(); // Store selected items with ID as key
        this.debounceTimeout = null;
    }

    connectedCallback() {
        // Get attributes
        const label = this.getAttribute('label') || 'Search Items';
        const placeholder = this.getAttribute('placeholder') || 'Search and add items...';
        const searchUrl = this.getAttribute('search-url') || '';
        const editUrlTemplate = this.getAttribute('edit-url-template') || '';
        const inputName = this.getAttribute('input-name') || 'selected_items';
        const searchDelay = parseInt(this.getAttribute('search-delay') || '300');
        const minChars = parseInt(this.getAttribute('min-chars') || '2');
        const maxResults = parseInt(this.getAttribute('max-results') || '10');
        const allowEdit = this.hasAttribute('allow-edit');
        const allowRemove = this.hasAttribute('allow-remove') !== false; // Default true
        const showBadges = this.hasAttribute('show-badges') !== false; // Default true
        const badgeVariant = this.getAttribute('badge-variant') || 'secondary';
        const noResultsText = this.getAttribute('no-results-text') || 'No items found!';
        const errorText = this.getAttribute('error-text') || 'Error searching items';
        
        // Pre-selected items from attribute or existing HTML
        const preSelected = this.getAttribute('pre-selected');
        
        // Event handlers
        const onSelectFn = this.getAttribute('data-onselect');
        const onRemoveFn = this.getAttribute('data-onremove');
        const onSearchFn = this.getAttribute('data-onsearch');
        const onErrorFn = this.getAttribute('data-onerror');

        // Store config
        this.config = {
            label, placeholder, searchUrl, editUrlTemplate, inputName,
            searchDelay, minChars, maxResults, allowEdit, allowRemove,
            showBadges, badgeVariant, noResultsText, errorText,
            onSelectFn, onRemoveFn, onSearchFn, onErrorFn
        };

        // Create the HTML structure
        this.innerHTML = `
            <div class="smart-search-container">
                <label class="form-label smart-search-label">${label}</label>
                <div class="smart-search-input-wrapper position-relative">
                    <input type="text" 
                           class="form-control smart-search-input" 
                           placeholder="${placeholder}"
                           autocomplete="off">
                    <div class="smart-search-spinner d-none">
                        <div class="spinner-border spinner-border-sm" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                    </div>
                </div>
                <div class="smart-search-results list-group mt-2"></div>
                ${showBadges ? `<div class="smart-search-selected mt-2" style="min-height: 1rem;"></div>` : ''}
                <div class="smart-search-hidden-inputs"></div>
            </div>
        `;

        // Get DOM elements with null checks
        this.input = this.querySelector('.smart-search-input');
        this.results = this.querySelector('.smart-search-results');
        this.selected = this.querySelector('.smart-search-selected');
        this.hiddenInputs = this.querySelector('.smart-search-hidden-inputs');
        this.spinner = this.querySelector('.smart-search-spinner');

        // Ensure all elements exist before proceeding
        if (!this.input || !this.results || !this.hiddenInputs) {
            console.error('SmartSearchInput: Required DOM elements not found');
            return;
        }

        // Attach events
        this.attachEvents();

        // Load pre-selected items after events are attached
        if (preSelected) {
            try {
                const items = JSON.parse(preSelected);
                items.forEach(item => this.addSelectedItem(item));
            } catch (e) {
                console.warn('Invalid pre-selected JSON:', preSelected);
            }
        }
        
        // Add styles
        this.addStyles();
    }

    attachEvents() {
        // Null check for input element
        if (!this.input) {
            console.error('SmartSearchInput: Input element not found');
            return;
        }

        // Search input event
        this.input.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            
            // Clear previous timeout
            if (this.debounceTimeout) {
                clearTimeout(this.debounceTimeout);
            }

            if (query.length >= this.config.minChars) {
                this.showSpinner(true);
                this.debounceTimeout = setTimeout(() => {
                    this.performSearch(query);
                }, this.config.searchDelay);
            } else {
                this.clearResults();
                this.showSpinner(false);
            }
        });

        // Hide results when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.contains(e.target)) {
                this.clearResults();
            }
        });

        // Handle keyboard navigation
        this.input.addEventListener('keydown', (e) => {
            const items = this.results.querySelectorAll('.list-group-item-action');
            const activeItem = this.results.querySelector('.active');
            
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                const next = activeItem ? activeItem.nextElementSibling : items[0];
                if (next) {
                    if (activeItem) activeItem.classList.remove('active');
                    next.classList.add('active');
                }
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                const prev = activeItem ? activeItem.previousElementSibling : items[items.length - 1];
                if (prev) {
                    if (activeItem) activeItem.classList.remove('active');
                    prev.classList.add('active');
                }
            } else if (e.key === 'Enter') {
                e.preventDefault();
                if (activeItem) {
                    activeItem.click();
                }
            } else if (e.key === 'Escape') {
                this.clearResults();
                this.input.blur();
            }
        });
    }

    async performSearch(query) {
        try {
            // Call custom search handler if provided
            if (this.config.onSearchFn && window[this.config.onSearchFn]) {
                const customResults = await window[this.config.onSearchFn](query);
                if (customResults) {
                    this.displayResults(customResults);
                    this.showSpinner(false);
                    return;
                }
            }

            // Default AJAX search
            if (!this.config.searchUrl) {
                console.warn('No search URL or custom search handler provided');
                this.showSpinner(false);
                return;
            }

            const response = await fetch(`${this.config.searchUrl}?q=${encodeURIComponent(query)}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.displayResults(data);

        } catch (error) {
            console.error('Search error:', error);
            this.showError(this.config.errorText);
            
            // Call error handler
            if (this.config.onErrorFn && window[this.config.onErrorFn]) {
                window[this.config.onErrorFn](error);
            }
        } finally {
            this.showSpinner(false);
        }
    }

    displayResults(data) {
        this.results.innerHTML = '';

        if (!data || data.length === 0) {
            this.results.innerHTML = `
                <div class="list-group-item text-danger">
                    <i class="ph ph-warning-circle me-2"></i>
                    ${this.config.noResultsText}
                </div>
            `;
            return;
        }

        // Limit results
        const limitedData = data.slice(0, this.config.maxResults);

        limitedData.forEach((item, index) => {
            // Skip if already selected
            if (this.selectedItems.has(item.id.toString())) {
                return;
            }

            const resultElement = document.createElement('a');
            resultElement.href = '#';
            resultElement.classList.add('list-group-item', 'list-group-item-action', 'smart-search-result');
            resultElement.dataset.itemId = item.id;
            
            // Create result content
            resultElement.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <div class="result-content">
                        <div class="result-title">${this.escapeHtml(item.title || item.name || item.label || 'Untitled')}</div>
                        ${item.description ? `<div class="result-description text-muted small">${this.escapeHtml(item.description)}</div>` : ''}
                    </div>
                    <i class="ph ph-plus text-primary"></i>
                </div>
            `;

            // Add click handler
            resultElement.addEventListener('click', (e) => {
                e.preventDefault();
                this.selectItem(item);
            });

            // Add hover effect for keyboard navigation
            resultElement.addEventListener('mouseenter', () => {
                this.results.querySelector('.active')?.classList.remove('active');
                resultElement.classList.add('active');
            });

            this.results.appendChild(resultElement);
        });
    }

    selectItem(item) {
        console.log('Selecting item:', item); // Debug log
        
        // Check if already selected
        if (this.selectedItems.has(item.id.toString())) {
            console.log('Item already selected:', item.id);
            return;
        }

        // Add to selected items
        this.selectedItems.set(item.id.toString(), item);
        console.log('Added to selectedItems map. Total items:', this.selectedItems.size);
        
        // Create visual representation if badges are enabled
        if (this.config.showBadges && this.selected) {
            console.log('Creating badge for item:', item);
            this.createSelectedBadge(item);
        } else {
            console.log('Badges disabled or selected container not found. showBadges:', this.config.showBadges, 'selected element:', !!this.selected);
        }

        // Create hidden input
        this.createHiddenInput(item);
        console.log('Created hidden input for item:', item.id);

        // Clear search
        this.input.value = '';
        this.clearResults();

        // Call custom select handler
        if (this.config.onSelectFn && window[this.config.onSelectFn]) {
            window[this.config.onSelectFn](item, this.getSelectedItems());
        }

        // Dispatch custom event
        this.dispatchEvent(new CustomEvent('itemSelected', {
            detail: { item, allSelected: this.getSelectedItems() }
        }));
        
        console.log('Item selection completed. Selected items:', this.getSelectedItems());
    }

    createSelectedBadge(item) {
        console.log('Creating badge for:', item);
        console.log('Selected element exists:', !!this.selected);
        
        if (!this.selected) {
            console.error('Selected container element not found');
            return;
        }

        const badge = document.createElement('span');
        badge.classList.add('badge', `bg-${this.config.badgeVariant}`, 'me-1', 'mb-1', 'smart-selected-item');
        badge.dataset.itemId = item.id;
        
        const title = item.title || item.name || item.label || 'Untitled';
        console.log('Badge title:', title);
        
        const editButton = this.config.allowEdit && this.config.editUrlTemplate ? 
            `<a href="${this.config.editUrlTemplate.replace('{id}', item.id)}" class="btn btn-sm btn-outline-light ms-1 py-0">Edit</a>` : '';
        
        const removeButton = this.config.allowRemove ? 
            `<button type="button" class="btn btn-sm btn-outline-light ms-1 py-0 px-1 border-0 remove-item-btn" data-item-id="${item.id}" aria-label="Remove">&times;</button>` : '';

        badge.innerHTML = `
            <span class="item-title">${this.escapeHtml(title)}</span>
            ${editButton}
            ${removeButton}
        `;

        // Add event listener for remove button
        const removeBtn = badge.querySelector('.remove-item-btn');
        if (removeBtn) {
            removeBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.removeSelectedItem(item.id);
            });
        }

        this.selected.appendChild(badge);
        console.log('Badge created and added to DOM');
    }

    createHiddenInput(item) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = this.config.inputName;
        input.value = item.id;
        input.dataset.itemId = item.id;
        this.hiddenInputs.appendChild(input);
    }

    removeSelectedItem(itemId) {
        const id = itemId.toString();
        
        if (!this.selectedItems.has(id)) {
            return;
        }

        const item = this.selectedItems.get(id);
        
        // Remove from selected items
        this.selectedItems.delete(id);

        // Remove badge
        const badge = this.selected?.querySelector(`[data-item-id="${id}"]`);
        if (badge) {
            badge.remove();
        }

        // Remove hidden input
        const hiddenInput = this.hiddenInputs.querySelector(`[data-item-id="${id}"]`);
        if (hiddenInput) {
            hiddenInput.remove();
        }

        // Call custom remove handler
        if (this.config.onRemoveFn && window[this.config.onRemoveFn]) {
            window[this.config.onRemoveFn](item, this.getSelectedItems());
        }

        // Dispatch custom event
        this.dispatchEvent(new CustomEvent('itemRemoved', {
            detail: { item, allSelected: this.getSelectedItems() }
        }));
    }

    addSelectedItem(item) {
        if (!item.id) {
            console.warn('Item must have an id property:', item);
            return;
        }
        
        this.selectItem(item);
    }

    clearResults() {
        this.results.innerHTML = '';
    }

    showSpinner(show) {
        if (show) {
            this.spinner.classList.remove('d-none');
        } else {
            this.spinner.classList.add('d-none');
        }
    }

    showError(message) {
        this.results.innerHTML = `
            <div class="list-group-item text-danger">
                <i class="ph ph-x-circle me-2"></i>
                ${message}
            </div>
        `;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Public API methods
    getSelectedItems() {
        return Array.from(this.selectedItems.values());
    }

    getSelectedIds() {
        return Array.from(this.selectedItems.keys());
    }

    clearSelected() {
        const ids = Array.from(this.selectedItems.keys());
        ids.forEach(id => this.removeSelectedItem(id));
    }

    setSelectedItems(items) {
        this.clearSelected();
        items.forEach(item => this.addSelectedItem(item));
    }

    focus() {
        this.input.focus();
    }

    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .smart-search-container {
                position: relative;
            }

            .smart-search-label {
                font-weight: 500;
                margin-bottom: 0.5rem;
                color: #374151;
            }

            .smart-search-input-wrapper {
                position: relative;
            }

            .smart-search-input {
                padding-right: 2.5rem;
            }

            .smart-search-spinner {
                position: absolute;
                right: 10px;
                top: 50%;
                transform: translateY(-50%);
                z-index: 10;
            }

            .smart-search-results {
                position: absolute;
                z-index: 1000;
                width: 100%;
                max-height: 300px;
                overflow-y: auto;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                border: 1px solid #e5e7eb;
                border-radius: 0.375rem;
                background: white;
            }

            .smart-search-results:empty {
                display: none;
            }

            .smart-search-result {
                border: none;
                transition: all 0.15s ease;
            }

            .smart-search-result:hover,
            .smart-search-result.active {
                background-color: #f3f4f6;
                color: #1f2937;
            }

            .result-content {
                flex: 1;
                min-width: 0;
            }

            .result-title {
                font-weight: 500;
                color: #1f2937;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            .result-description {
                font-size: 0.875rem;
                margin-top: 0.25rem;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            .smart-selected-item {
                display: inline-flex;
                align-items: center;
                padding: 0.375rem 0.75rem;
                font-size: 0.875rem;
                border-radius: 0.375rem;
                white-space: nowrap;
            }

            .smart-selected-item .item-title {
                max-width: 200px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }

            .smart-selected-item .btn {
                font-size: 0.75rem;
                line-height: 1;
                padding: 0.125rem 0.25rem;
            }

            .smart-search-selected {
                border: 1px dashed #e5e7eb;
                border-radius: 0.375rem;
                padding: 0.5rem;
                min-height: 2rem;
                background: #f9fafb;
            }

            .smart-search-selected:empty::before {
                content: "No items selected";
                color: #9ca3af;
                font-size: 0.875rem;
                font-style: italic;
            }

            /* Dark mode support */
            @media (prefers-color-scheme: dark) {
                .smart-search-label {
                    color: #f3f4f6;
                }

                .smart-search-results {
                    background: #1f2937;
                    border-color: #374151;
                }

                .smart-search-result {
                    color: #f3f4f6;
                    border-color: #374151;
                }

                .smart-search-result:hover,
                .smart-search-result.active {
                    background-color: #374151;
                    color: #f9fafb;
                }

                .result-title {
                    color: #f3f4f6;
                }
            }

            /* Bootstrap utilities */
            .d-none { display: none !important; }
            .d-flex { display: flex !important; }
            .justify-content-between { justify-content: space-between !important; }
            .align-items-center { align-items: center !important; }
            .text-muted { color: #6b7280 !important; }
            .text-primary { color: #3b82f6 !important; }
            .text-danger { color: #ef4444 !important; }
            .small { font-size: 0.875rem; }
            .me-1 { margin-right: 0.25rem; }
            .me-2 { margin-right: 0.5rem; }
            .ms-1 { margin-left: 0.25rem; }
            .mb-1 { margin-bottom: 0.25rem; }
            .mt-2 { margin-top: 0.5rem; }
            .py-0 { padding-top: 0; padding-bottom: 0; }
            .px-1 { padding-left: 0.25rem; padding-right: 0.25rem; }
            .position-relative { position: relative; }
            .visually-hidden { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }
        `;
        
        // Load Phosphor icons if not already loaded
        if (!document.querySelector('link[href*="phosphor"]')) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'https://cdnjs.cloudflare.com/ajax/libs/phosphor-icons/2.0.2/phosphor.min.css';
            document.head.appendChild(link);
        }
        
        this.appendChild(style);
    }
}

// Register the custom element
customElements.define('smart-search-input', SmartSearchInput);