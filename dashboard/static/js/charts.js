/**
 * Pricing Intelligence Dashboard
 *
 * Frontend chart layer.
 *
 * API contracts:
 *
 * GET /api/products
 *     -> Array<ProductPriceSummary>
 *
 * GET /api/merchant-frequency
 *     -> Array<MerchantFrequency>
 *
 * GET /api/largest-movements
 *     -> {
 *          largest_increases: Array<PriceMovement>,
 *          largest_decreases: Array<PriceMovement>
 *        }
 */


async function fetchJSON(url) {

    const response = await fetch(url);

    if (!response.ok) {

        throw new Error(
            `Request failed: ${response.status} ${response.statusText}`
        );
    }

    return response.json();
}


/**
 * Common Plotly configuration.
 */
function getPlotlyConfig() {

    return {
        responsive: true,
        displayModeBar: false
    };
}


/**
 * Common dashboard chart layout.
 */
function getBaseLayout(height = 400) {

    return {

        height: height,

        margin: {
            l: 70,
            r: 30,
            t: 30,
            b: 110
        },

        paper_bgcolor: "rgba(0,0,0,0)",

        plot_bgcolor: "rgba(0,0,0,0)",

        font: {
            family: "Inter, Arial, sans-serif",
            size: 12
        },

        xaxis: {
            automargin: true,
            gridcolor: "rgba(128,128,128,0.12)"
        },

        yaxis: {
            automargin: true,
            gridcolor: "rgba(128,128,128,0.12)"
        },

        legend: {
            orientation: "h",
            y: 1.08
        }
    };
}


/**
 * Format a product name for chart labels.
 *
 * Long product names make charts unreadable, so we
 * preserve the beginning while limiting display length.
 */
function formatProductLabel(name, maxLength = 42) {

    if (!name) {
        return "Unknown product";
    }

    if (name.length <= maxLength) {
        return name;
    }

    return `${name.substring(0, maxLength - 3)}...`;
}


/**
 * Load competitive pricing chart.
 *
 * Data source:
 *     /api/products
 *
 * Displays the products with the largest current
 * competitor price spreads.
 */
async function loadCompetitorChart() {

    const container = document.getElementById(
        "competitor-chart"
    );

    if (!container) {
        return;
    }

    try {

        const products = await fetchJSON(
            "/api/products"
        );

        if (!Array.isArray(products) || !products.length) {

            container.innerHTML =
                "<p>No competitor pricing data available.</p>";

            return;
        }

        const rows = products
            .filter(
                product =>
                    product.lowest_price !== null &&
                    product.highest_price !== null
            )
            .slice(0, 10);

        if (!rows.length) {

            container.innerHTML =
                "<p>No valid competitor pricing data available.</p>";

            return;
        }

        const labels = rows.map(
            product =>
                formatProductLabel(
                    product.product_name
                )
        );

        const lowestPrices = rows.map(
            product =>
                Number(product.lowest_price)
        );

        const highestPrices = rows.map(
            product =>
                Number(product.highest_price)
        );

        const traces = [

            {
                x: labels,

                y: lowestPrices,

                type: "bar",

                name: "Lowest price",

                hovertemplate:
                    "<b>%{x}</b><br>" +
                    "Lowest: $%{y:,.2f}" +
                    "<extra></extra>"
            },

            {
                x: labels,

                y: highestPrices,

                type: "bar",

                name: "Highest price",

                hovertemplate:
                    "<b>%{x}</b><br>" +
                    "Highest: $%{y:,.2f}" +
                    "<extra></extra>"
            }
        ];

        const layout = getBaseLayout(440);

        layout.barmode = "group";

        layout.xaxis = {

            automargin: true,

            tickangle: -35,

            gridcolor: "rgba(128,128,128,0.12)"
        };

        layout.yaxis = {

            title: "Price (USD)",

            tickprefix: "$",

            separatethousands: true,

            gridcolor: "rgba(128,128,128,0.12)"
        };

        await Plotly.newPlot(

            container,

            traces,

            layout,

            getPlotlyConfig()

        );

    } catch (error) {

        console.error(
            "Failed to load competitor pricing chart:",
            error
        );

        container.innerHTML =
            "<p>Unable to load competitor pricing data.</p>";
    }
}


/**
 * Load largest price movement chart.
 *
 * Data source:
 *     /api/largest-movements
 *
 * Positive values represent increases.
 * Negative values represent decreases.
 */
async function loadMovementChart() {

    const container = document.getElementById(
        "movement-chart"
    );

    if (!container) {
        return;
    }

    try {

        const result = await fetchJSON(
            "/api/largest-movements"
        );

        const increases =
            Array.isArray(result.largest_increases)
                ? result.largest_increases
                : [];

        const decreases =
            Array.isArray(result.largest_decreases)
                ? result.largest_decreases
                : [];

        const increaseRows = increases
            .filter(
                row =>
                    row.price_change !== null &&
                    Number(row.price_change) > 0
            )
            .slice(0, 5);

        const decreaseRows = decreases
            .filter(
                row =>
                    row.price_change !== null &&
                    Number(row.price_change) < 0
            )
            .slice(0, 5);

        const rows = [
            ...increaseRows,
            ...decreaseRows
        ];

        if (!rows.length) {

            container.innerHTML =
                "<p>No price movement data available.</p>";

            return;
        }

        const labels = rows.map(
            row =>
                formatProductLabel(
                    row.product_name
                )
        );

        const changes = rows.map(
            row =>
                Number(row.price_change)
        );

        const trace = {

            x: labels,

            y: changes,

            type: "bar",

            name: "Price movement",

            hovertemplate:
                "<b>%{x}</b><br>" +
                "Change: $%{y:,.2f}" +
                "<extra></extra>"
        };

        const layout = getBaseLayout(440);

        layout.xaxis = {

            automargin: true,

            tickangle: -35,

            gridcolor: "rgba(128,128,128,0.12)"
        };

        layout.yaxis = {

            title: "Price Change (USD)",

            tickprefix: "$",

            separatethousands: true,

            zeroline: true,

            zerolinewidth: 1,

            gridcolor: "rgba(128,128,128,0.12)"
        };

        await Plotly.newPlot(

            container,

            [trace],

            layout,

            getPlotlyConfig()

        );

    } catch (error) {

        console.error(
            "Failed to load price movement chart:",
            error
        );

        container.innerHTML =
            "<p>Unable to load price movement data.</p>";
    }
}


/**
 * Load merchant price-change frequency chart.
 *
 * Data source:
 *     /api/merchant-frequency
 *
 * The API is already sorted by price_change_rate
 * descending, so we display the top 15 merchants.
 */
async function loadMerchantChart() {

    const container = document.getElementById(
        "merchant-chart"
    );

    if (!container) {
        return;
    }

    try {

        const merchants = await fetchJSON(
            "/api/merchant-frequency"
        );

        if (!Array.isArray(merchants) || !merchants.length) {

            container.innerHTML =
                "<p>No merchant frequency data available.</p>";

            return;
        }

        const rows = merchants
            .filter(
                merchant =>
                    merchant.price_change_rate !== null
            )
            .slice(0, 15);

        if (!rows.length) {

            container.innerHTML =
                "<p>No valid merchant frequency data available.</p>";

            return;
        }

        const labels = rows.map(
            merchant =>
                merchant.merchant_name ||
                `Merchant ${merchant.merchant_id}`
        );

        const rates = rows.map(
            merchant =>
                Number(
                    merchant.price_change_rate
                )
        );

        const trace = {

            x: labels,

            y: rates,

            type: "bar",

            name: "Price change rate",

            hovertemplate:
                "<b>%{x}</b><br>" +
                "Change rate: %{y:.2f}%" +
                "<extra></extra>"
        };

        const layout = getBaseLayout(480);

        layout.xaxis = {

            automargin: true,

            tickangle: -40,

            gridcolor: "rgba(128,128,128,0.12)"
        };

        layout.yaxis = {

            title: "Price Change Rate (%)",

            ticksuffix: "%",

            rangemode: "tozero",

            gridcolor: "rgba(128,128,128,0.12)"
        };

        await Plotly.newPlot(

            container,

            [trace],

            layout,

            getPlotlyConfig()

        );

    } catch (error) {

        console.error(
            "Failed to load merchant frequency chart:",
            error
        );

        container.innerHTML =
            "<p>Unable to load merchant frequency data.</p>";
    }
}


/**
 * Main dashboard chart loader.
 */
async function loadDashboardCharts() {

    if (
        typeof Plotly === "undefined"
    ) {

        console.error(
            "Plotly.js is not loaded."
        );

        return;
    }

    await Promise.all([

        loadCompetitorChart(),

        loadMovementChart(),

        loadMerchantChart()

    ]);

    console.info(
        "Dashboard charts loaded successfully."
    );
}