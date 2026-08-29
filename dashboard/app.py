from flask import (
    Flask,
    jsonify,
    render_template,
    request,
)
from utils.config_manager import ConfigurationManager
from components.data_analysis import DataAnalysis
from logger.logger import get_logger


logger = get_logger(__name__)


def create_app() -> Flask:
    """
    Application factory for the analytics dashboard.
    """

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    # ==================================================
    # CONFIGURATION
    # ==================================================

    config_manager = ConfigurationManager()

    database_config = (
        config_manager.get_database_config()
    )

    data_analysis = DataAnalysis(
        database_config=database_config
    )

    # Store shared services in Flask config
    app.config["DATA_ANALYSIS"] = data_analysis

    # ==================================================
    # ROUTES
    # ==================================================

    @app.route("/")
    def index():
        """
        Dashboard overview page.
        """

        try:

            logger.info(
                "Loading dashboard overview..."
            )

            analysis = app.config["DATA_ANALYSIS"]

            competitor_summary = (
                analysis.get_competitor_price_summary()
            )

            merchant_frequency = (
                analysis.get_merchant_price_change_frequency()
            )

            price_history = (
                analysis.get_price_change_history()
            )

            # ------------------------------------------
            # Dashboard KPIs
            # ------------------------------------------

            total_products = (
                competitor_summary["product_id"]
                .nunique()
            )

            total_merchants = (
                price_history["merchant_id"]
                .nunique()
            )

            total_observations = len(
                price_history
            )

            total_price_changes = (
                price_history["price_change"]
                .notna()
                .sum()
            )

            logger.info(
                "Dashboard overview loaded successfully."
            )

            return render_template(
                "index.html",
                total_products=total_products,
                total_merchants=total_merchants,
                total_observations=total_observations,
                total_price_changes=total_price_changes,
            )

        except Exception as error:

            logger.exception(
                f"Failed to load dashboard overview: {error}"
            )

            return (
                "Dashboard failed to load.",
                500
            )

    @app.route("/products")
    def products():
        """
        Product explorer page.
        """

        try:

            logger.info(
                "Loading product explorer..."
            )

            analysis = app.config["DATA_ANALYSIS"]

            product_summary = (
                analysis.get_competitor_price_summary()
            )

            return render_template(
                "products.html",
                products=product_summary.to_dict(
                    orient="records"
                )
            )

        except Exception as error:

            logger.exception(
                f"Failed to load products: {error}"
            )

            return (
                "Product explorer failed to load.",
                500
            )

    @app.route("/product/<product_id>")
    def product_detail(product_id: str):
        """
        Product detail page.
        """

        try:

            logger.info(
                f"Loading product detail: {product_id}"
            )

            analysis = app.config["DATA_ANALYSIS"]

            summary = (
                analysis.get_competitor_price_summary(
                    product_id=product_id
                )
            )

            latest_prices = (
                analysis.get_latest_competitor_prices(
                    product_id=product_id
                )
            )

            price_history = (
                analysis.get_price_change_history(
                    product_id=product_id
                )
            )

            if summary.empty:

                return (
                    "Product not found.",
                    404
                )

            product = (
                summary.iloc[0]
                .to_dict()
            )

            competitors = (
                latest_prices
                .to_dict(
                    orient="records"
                )
            )

            history = (
                price_history
                .to_dict(
                    orient="records"
                )
            )

            return render_template(
                "product_detail.html",
                product=product,
                competitors=competitors,
                history=history,
            )

        except Exception as error:

            logger.exception(
                f"Failed to load product detail: "
                f"{error}"
            )

            return (
                "Product detail failed to load.",
                500
            )

    @app.route("/price-history")
    def price_history():
        """
        Price history page.
        """

        try:

            logger.info(
                "Loading price history..."
            )

            analysis = app.config["DATA_ANALYSIS"]

            product_id = request.args.get(
                "product_id"
            )

            history = (
                analysis.get_price_change_history(
                    product_id=product_id
                )
            )

            return render_template(
                "price_history.html",
                history=history.to_dict(
                    orient="records"
                )
            )

        except Exception as error:

            logger.exception(
                f"Failed to load price history: {error}"
            )

            return (
                "Price history failed to load.",
                500
            )
            
    @app.route("/api/overview")
    def api_overview():
        """
        Returns high-level dashboard metrics.
        """

        try:

            analysis = app.config["DATA_ANALYSIS"]

            competitor_summary = (
                analysis.get_competitor_price_summary()
            )

            price_history = (
                analysis.get_price_change_history()
            )

            response = {
                "total_products": int(
                    competitor_summary["product_id"]
                    .nunique()
                ),
                "total_merchants": int(
                    price_history["merchant_id"]
                    .nunique()
                ),
                "total_observations": int(
                    len(price_history)
                ),
                "total_price_changes": int(
                    price_history["price_change"]
                    .notna()
                    .sum()
                ),
            }

            return jsonify(response)

        except Exception as error:

            logger.exception(
                f"Overview API failed: {error}"
            )

            return jsonify(
                {
                    "error": "Failed to load overview metrics."
                }
            ), 500
            
    @app.route("/api/products")
    def api_products():
        """
        Returns product-level competitor summaries.
        """

        try:

            analysis = app.config["DATA_ANALYSIS"]

            products = (
                analysis.get_competitor_price_summary()
            )

            products = products.where(
                products.notna(),
                None
            )

            return jsonify(
                products.to_dict(
                    orient="records"
                )
            )

        except Exception as error:

            logger.exception(
                f"Products API failed: {error}"
            )

            return jsonify(
                {
                    "error": "Failed to load products."
                }
            ), 500
            
    @app.route("/api/product/<product_id>")
    def api_product(product_id: str):
        """
        Returns competitor and historical pricing
        information for a single product.
        """

        try:

            analysis = app.config["DATA_ANALYSIS"]

            summary = (
                analysis.get_competitor_price_summary(
                    product_id=product_id
                )
            )

            if summary.empty:

                return jsonify(
                    {
                        "error": "Product not found."
                    }
                ), 404

            latest_prices = (
                analysis.get_latest_competitor_prices(
                    product_id=product_id
                )
            )

            price_history = (
                analysis.get_price_change_history(
                    product_id=product_id
                )
            )

            summary = summary.where(
                summary.notna(),
                None
            )

            latest_prices = latest_prices.where(
                latest_prices.notna(),
                None
            )

            price_history = price_history.where(
                price_history.notna(),
                None
            )

            return jsonify(
                {
                    "summary": summary.iloc[0].to_dict(),
                    "competitors": latest_prices.to_dict(
                        orient="records"
                    ),
                    "price_history": price_history.to_dict(
                        orient="records"
                    ),
                }
            )

        except Exception as error:

            logger.exception(
                f"Product API failed for "
                f"{product_id}: {error}"
            )

            return jsonify(
                {
                    "error": "Failed to load product."
                }
            ), 500
            
    @app.route("/api/merchant-frequency")
    def api_merchant_frequency():
        """
        Returns merchant price-change statistics.
        """

        try:

            analysis = app.config["DATA_ANALYSIS"]

            merchants = (
                analysis
                .get_merchant_price_change_frequency()
            )

            merchants = merchants.where(
                merchants.notna(),
                None
            )

            return jsonify(
                merchants.to_dict(
                    orient="records"
                )
            )

        except Exception as error:

            logger.exception(
                f"Merchant frequency API failed: {error}"
            )

            return jsonify(
                {
                    "error": (
                        "Failed to load merchant statistics."
                    )
                }
            ), 500
            
    @app.route("/api/largest-movements")
    def api_largest_movements():
        """
        Returns the largest price increases
        and decreases.
        """

        try:

            analysis = app.config["DATA_ANALYSIS"]

            limit = request.args.get(
                "limit",
                default=10,
                type=int
            )

            if limit < 1:
                limit = 10

            result = (
                analysis.get_largest_price_movements(
                    limit=limit
                )
            )

            increases = (
                result["largest_increases"]
                .where(
                    result["largest_increases"].notna(),
                    None
                )
                .to_dict(orient="records")
            )

            decreases = (
                result["largest_decreases"]
                .where(
                    result["largest_decreases"].notna(),
                    None
                )
                .to_dict(orient="records")
            )

            return jsonify(
                {
                    "largest_increases": increases,
                    "largest_decreases": decreases,
                }
            )

        except Exception as error:

            logger.exception(
                f"Largest movements API failed: {error}"
            )

            return jsonify(
                {
                    "error": (
                        "Failed to load price movements."
                    )
                }
            ), 500
            
    @app.route("/api/price-history/<product_id>")
    def api_price_history(product_id: str):
        """
        Returns historical price observations
        for a product.
        """

        try:

            analysis = app.config["DATA_ANALYSIS"]

            history = (
                analysis.get_price_change_history(
                    product_id=product_id
                )
            )

            if history.empty:

                return jsonify(
                    {
                        "error": "Product history not found."
                    }
                ), 404

            history = history.astype(object).where(
                history.notna(),
                None
            )

            return jsonify(
                history.to_dict(
                    orient="records"
                )
            )

        except Exception as error:

            logger.exception(
                f"Price history API failed for "
                f"{product_id}: {error}"
            )

            return jsonify(
                {
                    "error": (
                        "Failed to load price history."
                    )
                }
            ), 500

    return app


# ======================================================
# APPLICATION ENTRY POINT
# ======================================================

app = create_app()


if __name__ == "__main__":

    logger.info(
        "Starting E-Commerce Price Intelligence Dashboard..."
    )

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )