// vis_logic.js — Reads config from embedded <script id="chart-config">

function applyDarkModeStyles(layout) {
    const isDarkMode = document.documentElement.getAttribute("data-theme") === "dark";
    return {
        ...layout,
        paper_bgcolor: isDarkMode ? "#1e1e1e" : "#f4f4f4",
        plot_bgcolor: isDarkMode ? "#222" : "#fff",
        font: { color: isDarkMode ? "#eee" : "#000" },
        xaxis: { ...layout.xaxis, gridcolor: isDarkMode ? "#444" : "#ddd" },
        yaxis: { ...layout.yaxis, gridcolor: isDarkMode ? "#444" : "#ddd" }
    };
}

function renderChart(containerId, jsonPath) {
    fetch(jsonPath)
        .then(res => res.json())
        .then(fig => {
            const layout = applyDarkModeStyles(fig.layout);
            Plotly.newPlot(containerId, fig.data, layout);
        });
}

const config = JSON.parse(document.getElementById("chart-config").textContent);

// Static charts TODO -> Consider allowing user to not include these
const staticDefaults = {
    "deck-statistics-1": "deck_statistics.json",
    "pitch-distribution": "pitch_distribution.json",
    "defense-distribution": "defense_distribution.json",
    "cost-distribution": "cost_distribution.json"
};

Object.entries({ ...staticDefaults, ...config.static }).forEach(([id, file]) => {
    renderChart(id, `./vis_data/${file}`);
});

// Shared dropdown setup
const sharedSelect = document.getElementById("shared-chart-select");
const groupSelect = document.getElementById("shared-group-select");
const sharedContainer = document.getElementById("cards-classification");

Object.entries(config.shared).forEach(([label, file]) => {
    const opt = document.createElement("option");
    opt.value = file;
    opt.text = label;
    sharedSelect.appendChild(opt);
});

["All", ...config.groups].forEach(group => {
    const opt = document.createElement("option");
    opt.value = group;
    opt.text = group;
    groupSelect.appendChild(opt);
});

function updateSharedChart() {
    const file = sharedSelect.value;
    const group = groupSelect.value;

    fetch(`./vis_data/${file}`)
        .then(res => res.json())
        .then(data => {
            const layout = applyDarkModeStyles(data.layout);
            let chartData = data.data;

            if (group !== "All") {
                chartData = data.data.filter(trace => trace.name === group);
                if (chartData.length > 0) {
                    const trace = chartData[0];
                    const sorted = trace.x.map((x, i) => ({ x, y: trace.y[i] }))
                        .sort((a, b) => b.y - a.y);
                    trace.x = sorted.map(p => p.x);
                    trace.y = sorted.map(p => p.y);
                }
            }
            Plotly.react("cards-classification", chartData, layout);
        });
}

sharedSelect.onchange = updateSharedChart;
groupSelect.onchange = updateSharedChart;
updateSharedChart();

// Number of cards
const typeSelect = document.getElementById("type-select");
const modeSelect = document.getElementById("mode-select");

Object.entries(config.number).forEach(([label, file]) => {
    const opt = document.createElement("option");
    opt.value = file;
    opt.text = label;
    typeSelect.appendChild(opt);
});

["Percentage", "Cumulative Increase"].forEach(mode => {
    const opt = document.createElement("option");
    opt.value = mode;
    opt.text = mode;
    modeSelect.appendChild(opt);
});

function updateNumberChart() {
    const file = typeSelect.value;
    const mode = modeSelect.value;

    fetch(`./vis_data/${file}`)
        .then(res => res.json())
        .then(data => {
            const layout = applyDarkModeStyles(data.layout);

            if (mode === "Cumulative Increase") {
                data.data.forEach(trace => {
                    let cumulativeY = [], sum = 0;
                    trace.y.forEach((y, i) => {
                        sum += trace.x[i] * y / 100;
                        cumulativeY.push(sum);
                    });
                    trace.y = cumulativeY;
                });
                layout.yaxis.title = "Expected Value: Cumulative Increase";
            } else {
                layout.yaxis.title = "Percentage of decks";
            }

            Plotly.react("number-of-cards", data.data, layout);
        });
}
typeSelect.onchange = updateNumberChart;
modeSelect.onchange = updateNumberChart;
updateNumberChart();
