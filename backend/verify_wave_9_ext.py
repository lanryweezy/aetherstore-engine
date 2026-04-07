import uuid
from sqlalchemy.orm import Session
from database import SessionLocal, init_db
from models import User, Brand, Product, UserActivity, UserLoyalty, LoyaltyTransaction, ProductReview
from analytics_engine import AnalyticsEngine

def verify_new_features():
    init_db()
    db = SessionLocal()

    try:
        # 1. Setup mock data
        user_id = str(uuid.uuid4())
        brand_id = str(uuid.uuid4())
        product_id = str(uuid.uuid4())
        store_id = str(uuid.uuid4())

        user = User(id=user_id, email=f"test_{user_id[:8]}@example.com", name="Test User", password_hash="hash")
        db.add(user)

        brand = Brand(id=brand_id, name="Test Brand", owner_user_id=user_id)
        db.add(brand)

        product = Product(id=product_id, brand_id=brand_id, name="Cool Shirt", price=49.99, stock_quantity=100)
        db.add(product)

        db.commit()
        print(f"Created mock user, brand, and product.")

        # 2. Verify Activity & Funnel
        activities = [
            UserActivity(user_id=user_id, store_id=store_id, activity_type="visit_store"),
            UserActivity(user_id=user_id, store_id=store_id, product_id=product_id, activity_type="view_product"),
            UserActivity(user_id=user_id, store_id=store_id, product_id=product_id, activity_type="try_on"),
            UserActivity(user_id=user_id, store_id=store_id, product_id=product_id, activity_type="add_to_cart"),
            UserActivity(user_id=user_id, store_id=store_id, product_id=product_id, activity_type="purchase"),
        ]
        db.add_all(activities)
        db.commit()

        analytics = AnalyticsEngine()
        funnel = analytics.get_conversion_funnel(store_id=store_id)
        print(f"Conversion Funnel for store: {funnel['funnel']}")
        assert len(funnel['funnel']) == 5
        assert funnel['total_conversions'] == 1

        # 3. Verify Loyalty
        loyalty = UserLoyalty(user_id=user_id, points_balance=100, total_earned=100)
        db.add(loyalty)
        transaction = LoyaltyTransaction(user_id=user_id, amount=100, reason="purchase")
        db.add(transaction)
        db.commit()

        check_loyalty = db.query(UserLoyalty).filter_by(user_id=user_id).first()
        print(f"User Loyalty: {check_loyalty.points_balance} points, Tier: {check_loyalty.tier}")
        assert check_loyalty.points_balance == 100

        # 4. Verify Reviews
        review = ProductReview(user_id=user_id, product_id=product_id, rating=5, comment="Amazing!")
        db.add(review)
        db.commit()

        check_review = db.query(ProductReview).filter_by(product_id=product_id).first()
        print(f"Product Review: {check_review.rating} stars - {check_review.comment}")
        assert check_review.rating == 5

        print("All new backend features verified successfully!")

    finally:
        db.close()

if __name__ == "__main__":
    verify_new_features()
