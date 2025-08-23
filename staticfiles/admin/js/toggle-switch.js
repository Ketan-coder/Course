document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('input[type=checkbox]').forEach(function (checkbox) {
        if (!checkbox.nextElementSibling || checkbox.nextElementSibling.tagName.toLowerCase() !== 'label') {
            const label = document.createElement('label');
            checkbox.parentNode.insertBefore(label, checkbox.nextSibling);
        }
    });
});
