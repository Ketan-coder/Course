# SmartInput Component Documentation

## Overview
SmartInput is a powerful custom HTML web component that provides a unified interface for various input types including text, textarea, select, datepicker, file upload, checkbox, switch, and radio buttons. It includes built-in validation, custom styling, and event handling.

## Dependencies
- **Bootstrap 5** - For styling classes
- **Phosphor Icons** - For icons (e.g., calendar, file icons)

## Basic Usage

```html
<script src="smart-input.js"></script>
<smart-input type="text" name="username" label="Username" required></smart-input>
```

## Common Attributes

| Attribute | Description | Default | Example |
|-----------|-------------|---------|---------|
| `type` | Input type | `text` | `text`, `select`, `datepicker`, `file`, etc. |
| `name` | Form field name | `input` | `username` |
| `label` | Display label | `''` | `Username` |
| `value` | Initial value | `''` | `john_doe` |
| `required` | Makes field required | `false` | `required` |
| `placeholder` | Placeholder text | `''` | `Enter your name` |
| `data-error` | Custom error message | `Invalid {label}` | `Username is required` |

## Event Handlers

| Attribute | Description | Example |
|-----------|-------------|---------|
| `data-oninput` | Function called on input | `data-oninput="handleInput"` |
| `data-onclick` | Function called on click | `data-onclick="handleClick"` |
| `data-onchange` | Function called on change | `data-onchange="handleChange"` |

## Input Types

### 1. Text Input

```html
<smart-input 
    type="text" 
    name="username" 
    label="Username" 
    placeholder="Enter username"
    required>
</smart-input>
```

**Supported text types:**
- `text` (default)
- `email`
- `password`
- `number`
- `tel`
- `url`

### 2. Textarea

```html
<smart-input 
    type="textarea" 
    name="message" 
    label="Message" 
    rows="5"
    placeholder="Enter your message"
    required>
</smart-input>
```

**Additional attributes:**
- `rows` - Number of visible rows (default: 4)

### 3. Select Dropdown

```html
<smart-input 
    type="select" 
    name="status" 
    label="Status" 
    value="pending"
    data-options='[
        {"id": "pending", "name": "Pending"}, 
        {"id": "completed", "name": "Completed"}, 
        {"id": "failed", "name": "Failed"}
    ]'
    required>
</smart-input>
```

**Additional attributes:**
- `data-options` - JSON array of options `[{"id": "value", "name": "Display Text"}]`
- `multiple` - Allow multiple selections
- `data-url` - URL for dynamic options with search

**Dynamic Select with Search:**
```html
<smart-input 
    type="select" 
    name="user" 
    label="Select User" 
    data-url="/api/users"
    required>
</smart-input>
```

### 4. Date Picker

```html
<smart-input 
    type="datepicker" 
    name="birthdate" 
    label="Birth Date" 
    value="15-03-1990"
    min-date="01-01-1950"
    max-date="31-12-2010"
    required>
</smart-input>
```

**Additional attributes:**
- `min-date` - Minimum allowed date (dd-mm-yyyy format)
- `max-date` - Maximum allowed date (dd-mm-yyyy format)
- `date-format` - Currently supports dd-mm-yyyy only

**Date Format:**
- Input/Output: `dd-mm-yyyy` (e.g., "15-03-1990")
- Display: Human readable (e.g., "15 March 1990")

### 5. File Upload

```html
<smart-input 
    type="file" 
    name="documents" 
    label="Upload Documents" 
    allowed-types="documents"
    max-size="5"
    max-files="3"
    required>
</smart-input>
```

**Additional attributes:**
- `allowed-types` - File type restriction
- `max-size` - Maximum file size in MB
- `max-files` - Maximum number of files (default: 1)
- `accept` - Custom file types (overrides allowed-types)

**Allowed Types:**
- `images` - All image formats
- `videos` - All video formats
- `documents` - PDF, DOC, DOCX, TXT, RTF
- `spreadsheets` - XLS, XLSX, CSV
- `presentations` - PPT, PPTX
- `archives` - ZIP, RAR, 7Z, TAR, GZ
- `audio` - All audio formats

**Multiple Files:**
```html
<smart-input 
    type="file" 
    name="images" 
    label="Upload Images" 
    allowed-types="images"
    max-files="5"
    max-size="10">
</smart-input>
```

### 6. Checkbox

```html
<smart-input 
    type="checkbox" 
    name="agree" 
    label="I agree to terms and conditions" 
    value="true">
</smart-input>
```

**Value handling:**
- Checked: `true`, `"true"`, `"1"`
- Unchecked: `false`, `"false"`, `"0"`

### 7. Switch (Toggle)

```html
<smart-input 
    type="switch" 
    name="notifications" 
    label="Enable Notifications" 
    value="true"
    is-big>
</smart-input>
```

**Additional attributes:**
- `is-big` - Large switch
- `is-medium` - Medium switch (default)
- `is-small` - Small switch
- `selected-value` - Alternative to value attribute

**Switch Sizes:**
```html
<!-- Small switch -->
<smart-input type="switch" name="small" label="Small" is-small>

<!-- Medium switch (default) -->
<smart-input type="switch" name="medium" label="Medium" is-medium>

<!-- Large switch -->
<smart-input type="switch" name="large" label="Large" is-big>
```

### 8. Radio Buttons

```html
<smart-input 
    type="radio" 
    name="priority" 
    label="Priority" 
    value="medium"
    data-options='[
        {"id": "low", "name": "Low Priority"}, 
        {"id": "medium", "name": "Medium Priority"}, 
        {"id": "high", "name": "High Priority"}
    ]'
    required>
</smart-input>
```

## JavaScript API

### Properties

```javascript
const input = document.querySelector('smart-input[name="username"]');

// Get/Set value
console.log(input.value);
input.value = "new_value";

// Get input element
const actualInput = input.getInputElement();

// Get hidden input (for datepicker)
const hiddenInput = input.getHiddenInput();
```

### Methods

```javascript
// Focus the input
input.focus();

// Validate the input
const isValid = input.validate();

// For file inputs, get selected files
if (input.getAttribute('type') === 'file') {
    const files = input.value; // Returns FileList
}
```

### Value Handling by Type

| Type | Get Value | Set Value | Returns |
|------|-----------|-----------|---------|
| text, email, etc. | `input.value` | `input.value = "text"` | String |
| textarea | `input.value` | `input.value = "text"` | String |
| select | `input.value` | `input.value = "option_id"` | String |
| datepicker | `input.value` | `input.value = "15-03-1990"` | String (dd-mm-yyyy) |
| file | `input.value` | Cannot set | FileList |
| checkbox/switch | `input.value` | `input.value = true` | Boolean |
| radio | `input.value` | `input.value = "option_id"` | String |

## Form Integration

```html
<form id="myForm">
    <smart-input 
        type="text" 
        name="username" 
        label="Username" 
        required>
    </smart-input>
    
    <smart-input 
        type="select" 
        name="status" 
        label="Status"
        data-options='[{"id": "active", "name": "Active"}, {"id": "inactive", "name": "Inactive"}]'
        required>
    </smart-input>
    
    <smart-input 
        type="datepicker" 
        name="date" 
        label="Date" 
        required>
    </smart-input>
    
    <button type="submit">Submit</button>
</form>

<script>
document.getElementById('myForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Validate all smart inputs
    const inputs = this.querySelectorAll('smart-input');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.validate()) {
            isValid = false;
        }
    });
    
    if (isValid) {
        // Get form data
        const formData = new FormData(this);
        console.log('Form data:', Object.fromEntries(formData));
    }
});
</script>
```

## Event Handling Examples

### Custom Event Handlers

```javascript
// Define global functions for event handling
function handleStatusChange(event) {
    console.log('Status changed to:', event.target.value);
}

function handleUsernameInput(event) {
    console.log('Username input:', event.target.value);
}

function handleFileUpload(event) {
    console.log('Files selected:', event.target.files.length);
}
```

```html
<smart-input 
    type="select" 
    name="status" 
    label="Status"
    data-onchange="handleStatusChange"
    data-options='[{"id": "active", "name": "Active"}]'>
</smart-input>

<smart-input 
    type="text" 
    name="username" 
    label="Username"
    data-oninput="handleUsernameInput">
</smart-input>

<smart-input 
    type="file" 
    name="upload" 
    label="Upload File"
    data-onchange="handleFileUpload">
</smart-input>
```

## Styling and Customization

The component uses Bootstrap 5 classes and includes custom CSS for animations and file uploads. You can override styles:

```css
/* Custom validation styles */
.smart-input .is-invalid {
    border-color: #dc3545 !important;
}

/* Custom file upload styling */
.smart-input .file-info {
    background-color: #f0f0f0;
    border: 2px dashed #ccc;
}

/* Custom switch colors */
.smart-input .form-check-input:checked {
    background-color: #28a745;
    border-color: #28a745;
}
```

## Complete Example

```html
<!DOCTYPE html>
<html>
<head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/phosphor-icons@1.4.1/src/css/phosphor.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <form id="userForm">
            <div class="row">
                <div class="col-md-6">
                    <smart-input 
                        type="text" 
                        name="name" 
                        label="Full Name" 
                        required 
                        placeholder="Enter your full name">
                    </smart-input>
                </div>
                
                <div class="col-md-6">
                    <smart-input 
                        type="email" 
                        name="email" 
                        label="Email" 
                        required 
                        placeholder="Enter your email">
                    </smart-input>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <smart-input 
                        type="datepicker" 
                        name="birthdate" 
                        label="Birth Date" 
                        min-date="01-01-1950"
                        max-date="31-12-2005">
                    </smart-input>
                </div>
                
                <div class="col-md-6">
                    <smart-input 
                        type="select" 
                        name="country" 
                        label="Country" 
                        required
                        data-options='[
                            {"id": "us", "name": "United States"}, 
                            {"id": "uk", "name": "United Kingdom"}, 
                            {"id": "ca", "name": "Canada"}
                        ]'>
                    </smart-input>
                </div>
            </div>
            
            <div class="row">
                <div class="col-12">
                    <smart-input 
                        type="textarea" 
                        name="message" 
                        label="Message" 
                        rows="4" 
                        placeholder="Enter your message">
                    </smart-input>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <smart-input 
                        type="file" 
                        name="resume" 
                        label="Upload Resume" 
                        allowed-types="documents" 
                        max-size="5">
                    </smart-input>
                </div>
                
                <div class="col-md-6">
                    <smart-input 
                        type="switch" 
                        name="newsletter" 
                        label="Subscribe to Newsletter" 
                        value="false">
                    </smart-input>
                </div>
            </div>
            
            <div class="row">
                <div class="col-12">
                    <smart-input 
                        type="checkbox" 
                        name="terms" 
                        label="I agree to the terms and conditions" 
                        required>
                    </smart-input>
                </div>
            </div>
            
            <button type="submit" class="btn btn-primary">Submit</button>
        </form>
    </div>
    
    <script src="smart-input.js"></script>
    <script>
        document.getElementById('userForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validate all inputs
            const inputs = this.querySelectorAll('smart-input');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.validate()) {
                    isValid = false;
                }
            });
            
            if (isValid) {
                const formData = new FormData(this);
                console.log('Form submitted:', Object.fromEntries(formData));
                alert('Form submitted successfully!');
            } else {
                alert('Please fix the errors before submitting.');
            }
        });
    </script>
</body>
</html>
```

## Troubleshooting

### Common Issues

1. **Select not showing selected value**
   - Fixed in the updated version
   - Ensure `data-options` JSON is valid
   - Check that `value` attribute matches an option `id`

2. **Date picker not working**
   - Ensure Phosphor Icons are loaded
   - Use dd-mm-yyyy format for dates
   - Check min-date and max-date constraints

3. **File upload validation errors**
   - Check `allowed-types` spelling
   - Verify `max-size` is reasonable
   - Ensure files match the allowed types

4. **Event handlers not firing**
   - Functions must be global (attached to `window`)
   - Check function names in attributes match exactly
   - Use browser console to check for errors

### Browser Compatibility
- Modern browsers supporting Custom Elements v1
- Chrome 67+, Firefox 63+, Safari 10.1+, Edge 79+

## Migration Notes

If upgrading from the original version:
- Select dropdowns now properly handle the `value` attribute
- File validation is more robust
- Better error handling for malformed JSON in `data-options`