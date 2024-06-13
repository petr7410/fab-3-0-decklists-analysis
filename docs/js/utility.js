document.addEventListener('DOMContentLoaded', () => {
    const tooltips = document.querySelectorAll('.tooltip');
    tooltips.forEach(tooltip => {
        const img = tooltip.querySelector('.tooltiptext img');
        if (img) {
            tooltip.addEventListener('mouseover', () => {
                if (!img.src) {
                    img.src = img.getAttribute('data-src');
                }
            });
        }
    });
});