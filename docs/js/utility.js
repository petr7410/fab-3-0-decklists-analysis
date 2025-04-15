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

            // Prevent default action on click
            tooltip.addEventListener('click', (event) => {
                event.preventDefault();
                event.stopPropagation();
            });
        }
    });
});

addEventListener("storage", (event) => {
    if (event.key === "theme") {
        document.documentElement.setAttribute("data-theme", localStorage.getItem("theme"));
    }
});

document.documentElement.setAttribute("data-theme", localStorage.getItem("theme"));
