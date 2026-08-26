/**
 * Pricing Intelligence Dashboard
 *
 * General frontend behavior.
 *
 * Chart rendering is intentionally kept in charts.js.
 */


/**
 * Display a loading state inside an element.
 */
function showLoading(element, message = "Loading...") {

    if (!element) {
        return;
    }

    element.innerHTML = `
        <div class="loading-state">
            <span class="loading-spinner"></span>
            <span>${message}</span>
        </div>
    `;
}


/**
 * Display an error state inside an element.
 */
function showError(element, message = "Unable to load data.") {

    if (!element) {
        return;
    }

    element.innerHTML = `
        <div class="error-state">
            <strong>Something went wrong</strong>
            <span>${message}</span>
        </div>
    `;
}


/**
 * Safely format a number.
 */
function formatNumber(value, decimals = 0) {

    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    return number.toLocaleString(
        "en-US",
        {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }
    );
}


/**
 * Safely format currency.
 */
function formatCurrency(value) {

    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    return number.toLocaleString(
        "en-US",
        {
            style: "currency",
            currency: "USD",
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }
    );
}


/**
 * Safely format percentage.
 */
function formatPercentage(value) {

    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    return `${number.toFixed(2)}%`;
}


/**
 * Attach a small navigation helper to product links.
 */
function initializeProductNavigation() {

    const productLinks =
        document.querySelectorAll(
            "[data-product-id]"
        );

    productLinks.forEach(
        link => {

            link.addEventListener(
                "click",
                function () {

                    const productId =
                        this.dataset.productId;

                    if (!productId) {
                        return;
                    }

                    console.debug(
                        "Opening product:",
                        productId
                    );
                }
            );

        }
    );
}


/**
 * Add a simple client-side search interaction
 * when a search input exists on the page.
 */
function initializeSearch() {

    const searchInput =
        document.querySelector(
            "[data-product-search]"
        );

    if (!searchInput) {
        return;
    }

    const searchableRows =
        document.querySelectorAll(
            "[data-searchable]"
        );

    searchInput.addEventListener(
        "input",
        function () {

            const query =
                this.value
                    .trim()
                    .toLowerCase();

            searchableRows.forEach(
                row => {

                    const searchableText =
                        (
                            row.dataset.searchable ||
                            row.textContent ||
                            ""
                        ).toLowerCase();

                    row.hidden =
                        query.length > 0 &&
                        !searchableText.includes(query);
                }
            );
        }
    );
}


/**
 * Mark the current navigation item as active.
 */
function initializeActiveNavigation() {

    const currentPath =
        window.location.pathname;

    const navigationLinks =
        document.querySelectorAll(
            ".sidebar-nav a[href]"
        );

    navigationLinks.forEach(
        link => {

            const href =
                link.getAttribute("href");

            if (!href) {
                return;
            }

            link.classList.toggle(
                "active",
                href === currentPath
            );
        }
    );
}


/**
 * Global dashboard initialization.
 */
function initializeDashboard() {

    initializeProductNavigation();

    initializeSearch();

    initializeActiveNavigation();

    console.debug(
        "Dashboard frontend initialized."
    );
}


document.addEventListener(
    "DOMContentLoaded",
    initializeDashboard
);

/**
 * Price History page
 *
 * Loads the product catalogue from /api/products
 * and historical observations from
 * /api/price-history/<product_id>.
 */
async function loadPriceHistoryPage() {

    const searchInput =
        document.getElementById("product-search");

    const selector =
        document.getElementById("product-selector");

    const tableBody =
        document.getElementById("price-history-body");

    if (!searchInput || !selector || !tableBody) {
        return;
    }

    let products = [];

    try {

        const response =
            await fetch("/api/products");

        if (!response.ok) {
            throw new Error(
                `Product API returned ${response.status}`
            );
        }

        products = await response.json();

        populateProductSelector(
            selector,
            products
        );

        searchInput.addEventListener(
            "input",
            function () {

                filterProductSelector(
                    selector,
                    products,
                    searchInput.value
                );

            }
        );

        selector.addEventListener(
            "change",
            function () {

                if (selector.value) {

                    loadSelectedProductHistory(
                        selector.value
                    );

                }

            }
        );

    } catch (error) {

        console.error(
            "Failed to load products:",
            error
        );

        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="table-loading">
                    Failed to load products.
                </td>
            </tr>
        `;
    }
}


/**
 * Populate product selector.
 */
function populateProductSelector(
    selector,
    products
) {

    selector.innerHTML = "";

    const defaultOption =
        document.createElement("option");

    defaultOption.value = "";
    defaultOption.textContent =
        "Select a product...";

    selector.appendChild(
        defaultOption
    );

    products.forEach(
        function (product) {

            const option =
                document.createElement("option");

            option.value =
                product.product_id;

            option.textContent =
                product.product_name ||
                product.product_id;

            selector.appendChild(
                option
            );

        }
    );
}


/**
 * Filter product selector based on search text.
 */
function filterProductSelector(
    selector,
    products,
    searchTerm
) {

    const query =
        searchTerm
            .trim()
            .toLowerCase();

    const currentValue =
        selector.value;

    selector.innerHTML = "";

    const defaultOption =
        document.createElement("option");

    defaultOption.value = "";
    defaultOption.textContent =
        query
            ? "Matching products..."
            : "Select a product...";

    selector.appendChild(
        defaultOption
    );

    products
        .filter(
            function (product) {

                const name =
                    String(
                        product.product_name || ""
                    ).toLowerCase();

                const id =
                    String(
                        product.product_id || ""
                    ).toLowerCase();

                return (
                    !query ||
                    name.includes(query) ||
                    id.includes(query)
                );

            }
        )
        .forEach(
            function (product) {

                const option =
                    document.createElement("option");

                option.value =
                    product.product_id;

                option.textContent =
                    product.product_name ||
                    product.product_id;

                selector.appendChild(
                    option
                );

            }
        );

    if (
        currentValue &&
        Array.from(selector.options)
            .some(
                option =>
                    option.value === currentValue
            )
    ) {

        selector.value =
            currentValue;

    }
}


/**
 * Load historical prices for selected product.
 */
async function loadSelectedProductHistory(
    productId
) {

    const tableBody =
        document.getElementById(
            "price-history-body"
        );

    if (!tableBody) {
        return;
    }

    tableBody.innerHTML = `
        <tr>
            <td colspan="6" class="table-loading">
                Loading price history...
            </td>
        </tr>
    `;

    try {

        const response =
            await fetch(
                `/api/price-history/${encodeURIComponent(productId)}`
            );

        if (!response.ok) {
            throw new Error(
                `History API returned ${response.status}`
            );
        }

        const history =
            await response.json();

        renderPriceHistory(
            history
        );

    } catch (error) {

        console.error(
            "Failed to load price history:",
            error
        );

        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="table-loading">
                    Failed to load price history.
                </td>
            </tr>
        `;
    }
}


/**
 * Render historical observations.
 */
function renderPriceHistory(
    history
) {

    const tableBody =
        document.getElementById(
            "price-history-body"
        );

    const summaryPanel =
        document.getElementById(
            "history-summary-panel"
        );

    if (!tableBody) {
        return;
    }

    if (!history || history.length === 0) {

        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="table-loading">
                    No price history available.
                </td>
            </tr>
        `;

        if (summaryPanel) {
            summaryPanel.style.display =
                "none";
        }

        return;
    }

    const changes =
        history.filter(
            record =>
                Number.isFinite(
                    Number(record.price_change)
                ) &&
                Number(record.price_change) !== 0
        );

    const increases =
        changes.filter(
            record =>
                Number(record.price_change) > 0
        );

    const decreases =
        changes.filter(
            record =>
                Number(record.price_change) < 0
        );

    updateHistorySummary(
        history,
        changes,
        increases,
        decreases
    );

    tableBody.innerHTML =
        history.map(
            function (record) {

                const previousPrice =
                    Number.isFinite(
                        Number(
                            record.previous_price
                        )
                    )
                        ? formatCurrency(
                            record.previous_price
                        )
                        : "—";

                const currentPrice =
                    Number.isFinite(
                        Number(record.price)
                    )
                        ? formatCurrency(
                            record.price
                        )
                        : "—";

                const change =
                    Number.isFinite(
                        Number(record.price_change)
                    )
                        ? formatSignedCurrency(
                            record.price_change
                        )
                        : "—";

                const percentage =
                    Number.isFinite(
                        Number(
                            record.price_change_percentage
                        )
                    )
                        ? formatPercentage(
                            record.price_change_percentage
                        )
                        : "—";

                const changeClass =
                    Number(record.price_change) > 0
                        ? "price-increase"
                        : Number(record.price_change) < 0
                            ? "price-decrease"
                            : "";

                return `
                    <tr>

                        <td>
                            <strong>
                                ${escapeHtml(
                                    record.merchant_name ||
                                    "Unknown merchant"
                                )}
                            </strong>
                        </td>

                        <td>
                            ${formatDate(
                                record.observed_at
                            )}
                        </td>

                        <td>
                            ${previousPrice}
                        </td>

                        <td class="price-cell">
                            ${currentPrice}
                        </td>

                        <td class="${changeClass}">
                            ${change}
                        </td>

                        <td class="${changeClass}">
                            ${percentage}
                        </td>

                    </tr>
                `;

            }
        ).join("");
}


/**
 * Update history KPI cards.
 */
function updateHistorySummary(
    history,
    changes,
    increases,
    decreases
) {

    const panel =
        document.getElementById(
            "history-summary-panel"
        );

    if (!panel) {
        return;
    }

    const productName =
        document.getElementById(
            "history-product-name"
        );

    const observations =
        document.getElementById(
            "history-observations"
        );

    const changeCount =
        document.getElementById(
            "history-changes"
        );

    const increaseCount =
        document.getElementById(
            "history-increases"
        );

    const decreaseCount =
        document.getElementById(
            "history-decreases"
        );

    if (productName) {

        productName.textContent =
            history[0].product_name ||
            "Selected Product";

    }

    if (observations) {
        observations.textContent =
            history.length;
    }

    if (changeCount) {
        changeCount.textContent =
            changes.length;
    }

    if (increaseCount) {
        increaseCount.textContent =
            increases.length;
    }

    if (decreaseCount) {
        decreaseCount.textContent =
            decreases.length;
    }

    panel.style.display =
        "block";
}


/**
 * Format currency safely.
 */
function formatCurrency(
    value
) {

    const number =
        Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    return new Intl.NumberFormat(
        "en-US",
        {
            style: "currency",
            currency: "USD"
        }
    ).format(number);
}


/**
 * Format signed currency.
 */
function formatSignedCurrency(
    value
) {

    const number =
        Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    if (number > 0) {

        return `+${formatCurrency(number)}`;

    }

    if (number < 0) {

        return `-${formatCurrency(
            Math.abs(number)
        )}`;

    }

    return formatCurrency(0);
}


/**
 * Format percentage.
 */
function formatPercentage(
    value
) {

    const number =
        Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    if (number > 0) {
        return `+${number.toFixed(2)}%`;
    }

    return `${number.toFixed(2)}%`;
}


/**
 * Format API date.
 */
function formatDate(
    value
) {

    if (!value) {
        return "—";
    }

    const date =
        new Date(value);

    if (
        Number.isNaN(
            date.getTime()
        )
    ) {
        return escapeHtml(
            String(value)
        );
    }

    return date.toLocaleString(
        "en-IN",
        {
            dateStyle: "medium",
            timeStyle: "short"
        }
    );
}


/**
 * Escape dynamic HTML values.
 */
function escapeHtml(
    value
) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}