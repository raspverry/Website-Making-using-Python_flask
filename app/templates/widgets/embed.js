(function() {
    'use strict';

    var containers = document.querySelectorAll('[data-widget]');

    containers.forEach(function(container) {
        var widgetId = container.getAttribute('data-widget');
        if (!widgetId) return;

        var iframe = document.createElement('iframe');
        iframe.src = '{{ config.APP_URL }}/widget/' + widgetId;
        iframe.style.width = '100%';
        iframe.style.border = 'none';
        iframe.style.overflow = 'hidden';
        iframe.setAttribute('scrolling', 'no');
        iframe.setAttribute('loading', 'lazy');
        iframe.title = 'TestiFlow Testimonials';

        // Auto-resize iframe based on content height
        iframe.onload = function() {
            try {
                var resizeObserver = new ResizeObserver(function() {
                    iframe.style.height = iframe.contentDocument.body.scrollHeight + 'px';
                });
                resizeObserver.observe(iframe.contentDocument.body);
            } catch(e) {
                // Fallback for cross-origin: use postMessage
                iframe.style.height = '500px';
            }
        };

        container.innerHTML = '';
        container.appendChild(iframe);
    });
})();
