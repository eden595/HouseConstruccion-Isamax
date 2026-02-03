function renderCharts() {
    // Chart 1: Average Line
    var averageLineEl = document.querySelector("#average-line");
    if (averageLineEl) {
        var averageLineOptions = {
            series: [
                { name: "Current Year", data: [800, 850, 780, 850, 860, 880, 900, 1000, 1200, 1400] },
                { name: "Prior Year", data: [880, 600, 630, 590, 660, 950, 800, 900, 1000, 1200] }
            ],
            chart: { height: 380, type: "area", toolbar: { show: false } },
            colors: ["#5b66eb", "#ffc107"],
            dataLabels: { enabled: false },
            stroke: { curve: "smooth", width: 2 },
            grid: { show: false },
            xaxis: {
                categories: ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Nov"],
                axisBorder: { show: false }
            },
            yaxis: {
                categories: ["$200","$400","$600","$800","$1k","$1.2K","$1.4K"],
                axisBorder: { show: false }
            },
            tooltip: { theme: "dark" }
        };
        new ApexCharts(averageLineEl, averageLineOptions).render();
    }

    // Chart 2: Average Bar
    var averageBarEl = document.querySelector("#average-bar");
    if (averageBarEl) {
        var averageBarOptions = {
            series: [
                { name: "Current Year", data: [44,55,57,56,61,58,63,60,66] },
                { name: "Prior Year", data: [76,85,101,98,87,105,91,114,94] }
            ],
            chart: { type: "bar", height: 350 },
            colors: ["#5b66eb", "#ffc107"],
            plotOptions: {
                bar: { horizontal: false, columnWidth: "55%", borderRadius: 5, borderRadiusApplication: "end" }
            },
            dataLabels: { enabled: false },
            stroke: { show: true, width: 2, colors: ["transparent"] },
            xaxis: { categories: ["Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct"] },
            fill: { opacity: 1 }
        };
        new ApexCharts(averageBarEl, averageBarOptions).render();
    }

    // GridJS Table
    var gridEl = document.getElementById("gridjs_sort-table");
    if (gridEl) {
        new gridjs.Grid({
            columns: [
                { name: "Date", formatter: e => gridjs.html(`<span class="text-muted">${e}</span>`) },
                { name: "Name", formatter: e => gridjs.html(`<span class="text-muted">${e}</span>`) },
                { name: "Amount", formatter: e => gridjs.html(`<span class="text-muted">${e}</span>`) }
            ],
            sort: true,
            data: [
                ["01 Feb 2024","Robert","$50.86"],
                ["03 Feb 2024","Smith","$76.53"],
                ["07 Feb 2024","Adam","$48.65"],
                ["08 Feb 2024","Teff","$100.00"],
                ["09 Feb 2024","John","$895.4"],
                ["01 Mar 2024","Lucy","$59.36"],
                ["02 Mar 2024","Daniel","$50.86"]
            ]
        }).render(gridEl);
    }

    // Chart 3: Product Statistics RadialBar
    var productStatsEl = document.querySelector("#product-statistics");
    if (productStatsEl) {
        var productStatsOptions = {
            series: [76,67,61],
            chart: { height: 330, type: "radialBar" },
            plotOptions: {
                radialBar: {
                    offsetY: 0,
                    startAngle: 0,
                    endAngle: 270,
                    hollow: { margin: 5, size: "30%", background: "transparent" },
                    track: { margin: 10 },
                    dataLabels: { name: { show: false }, value: { show: false } },
                    barLabels: {
                        enabled: true,
                        useSeriesColors: true,
                        offsetX: -8,
                        fontSize: "16px",
                        formatter: function (label, chart) {
                            return label + ":  " + chart.w.globals.series[chart.seriesIndex];
                        }
                    }
                }
            },
            colors: ["#5b66eb","#ffc107","#dc3545"],
            responsive: [{ breakpoint: 480, options: { legend: { show: false } } }]
        };
        new ApexCharts(productStatsEl, productStatsOptions).render();
    }
}

// Ejecutar con un pequeño delay para asegurar que el DOM esté listo
setTimeout(() => { renderCharts(); }, 250);
