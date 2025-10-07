import requests
import asyncio
from datetime import datetime, timedelta
from src.platforms.clickbank.services.clickbank_service import get_clickbank_creds

BASE_URL = "https://api.clickbank.com/rest/1.3"

async def fetch_orders_async(user_id: str, days: int = 30):
    """Fetch individual order data from ClickBank API with product details"""
    creds = await get_clickbank_creds(user_id)

    if not creds:
        raise Exception("ClickBank account not connected")

    headers = {
        "Authorization": f"Bearer {creds['api_key']}",
        "Content-Type": "application/json"
    }

    # Calculate date range for orders
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    params = {
        "account": creds['nickname'],
        "startDate": start_date.strftime("%Y-%m-%d"),
        "endDate": end_date.strftime("%Y-%m-%d")
    }

    r = requests.get(f"{BASE_URL}/orders2/list", headers=headers, params=params)
    if r.status_code != 200:
        raise Exception(f"ClickBank Orders API error: {r.text}")

    return r.json()

def extract_product_sales_data(orders_data: dict) -> list:
    """Extract product-level sales data from ClickBank orders response"""
    products = {}

    try:
        # ClickBank returns XML, but this assumes JSON conversion
        orders = orders_data.get("orders", [])

        for order in orders:
            line_items = order.get("lineItems", [])

            for item in line_items:
                sku = item.get("sku", "unknown")
                product_title = item.get("productTitle", "Unknown Product")

                if sku not in products:
                    products[sku] = {
                        "sku": sku,
                        "product_name": product_title,
                        "vendor": order.get("vendor", ""),
                        "total_sales": 0,
                        "total_revenue": 0.0,
                        "total_quantity": 0,
                        "orders": []
                    }

                # Aggregate product data
                customer_amount = float(item.get("customerAmount", 0))
                quantity = int(item.get("quantity", 1))

                products[sku]["total_sales"] += 1
                products[sku]["total_revenue"] += customer_amount
                products[sku]["total_quantity"] += quantity
                products[sku]["orders"].append({
                    "receipt": order.get("receipt", ""),
                    "transaction_time": order.get("transactionTime", ""),
                    "customer_amount": customer_amount,
                    "quantity": quantity
                })

    except Exception as e:
        print(f"Error extracting product sales data: {e}")

    return list(products.values())

async def get_user_product_performance(user_id: str, days: int = 30) -> dict:
    """Get comprehensive product performance data for a user"""
    try:
        # Fetch both summary analytics and detailed orders
        from src.platforms.clickbank.services.clickbank_service import fetch_sales_async

        summary_data = await fetch_sales_async(user_id, days)
        orders_data = await fetch_orders_async(user_id, days)

        # Extract product-level data
        product_sales = extract_product_sales_data(orders_data)

        return {
            "user_id": user_id,
            "platform": "clickbank",
            "summary_metrics": summary_data,
            "product_performance": product_sales,
            "period_days": days,
            "data_timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"Error getting user product performance: {e}")
        return {
            "user_id": user_id,
            "platform": "clickbank",
            "summary_metrics": {},
            "product_performance": [],
            "period_days": days,
            "error": str(e),
            "data_timestamp": datetime.now().isoformat()
        }