# clickbank_module/tasks.py
from worker import celery
from src.platforms.clickbank.services import clickbank_service
from src.core.database.session import database

@celery.task(name="tasks.sync_clickbank_sales")
def sync_clickbank_sales():
    """
    Nightly job: fetches sales for all connected ClickBank accounts
    and stores them in the DB.
    """
    # Get all users with ClickBank connected
    rows = database.fetch_all("SELECT user_id FROM clickbank_accounts")
    for row in rows:
        user_id = row["user_id"]
        try:
            sales = clickbank_service.fetch_sales(user_id, days=1)
            # Store each transaction in sales table
            for s in sales.get("transactions", []):
                database.execute(
                    """
                    INSERT INTO clickbank_sales
                        (user_id, transaction_id, product_title, amount, commission, transaction_date, type)
                    VALUES
                        (:user_id, :transaction_id, :product_title, :amount, :commission, :transaction_date, :type)
                    ON CONFLICT (transaction_id) DO NOTHING
                    """,
                    {
                        "user_id": user_id,
                        "transaction_id": s["transaction_id"],
                        "product_title": s["product_title"],
                        "amount": s["amount"],
                        "commission": s["commission"],
                        "transaction_date": s["transaction_date"],
                        "type": s["type"],
                    },
                )
        except Exception as e:
            print(f"Error syncing user {user_id}: {e}")
