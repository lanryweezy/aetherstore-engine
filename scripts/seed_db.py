import sys
import os
import uuid
from datetime import datetime

# Add backend to path to import database and models
sys.path.append(os.path.join(os.getcwd(), "backend"))

from database import SessionLocal, Base, engine
from models import ProductDB, StoreDB
from schemas import Product, Store

def seed_database():
    print("⏳ Seeding AetherStore Persistent Database...")
    db = SessionLocal()
    
    try:
        # 1. Clear existing data (Optional, for clean seed)
        db.query(ProductDB).delete()
        db.query(StoreDB).delete()
        
        # 2. Define Initial Collection
        initial_products = [
            {
                "id": "prod_exo_shell_001",
                "name": "Cyberpunk Exo-Shell",
                "description": "Ultra-lightweight protective shell with reactive lighting and integrated haptics.",
                "price": 299.99,
                "brand_id": "brand_aether_labs",
                "category": "Outerwear",
                "size_chart": {"S": {"chest": 90}, "M": {"chest": 100}, "L": {"chest": 110}},
                "material": "Bio-Polymer Weave",
                "colors": ["Neon Blue", "Matte Black"],
                "dimensions": {"width": 50, "height": 75, "depth": 10},
                "asset_urls": {
                    "3d_model": "/assets/models/exo_shell.glb",
                    "image": "/assets/images/exo_shell.jpg",
                    "splat": "/data/splats/exo_shell.ply"
                }
            },
            {
                "id": "prod_neon_hoodie_002",
                "name": "Neon Weave Hoodie",
                "description": "Smart-fabric hoodie that adapts to body temperature with fiber-optic stitching.",
                "price": 159.00,
                "brand_id": "brand_aether_labs",
                "category": "Tops",
                "size_chart": {"M": {"chest": 105}, "L": {"chest": 115}},
                "material": "Thermal-Adaptive Knit",
                "colors": ["Electric Lime", "Slate Grey"],
                "dimensions": {"width": 55, "height": 70, "depth": 5},
                "asset_urls": {
                    "3d_model": "/assets/models/neon_hoodie.glb",
                    "image": "/assets/images/neon_hoodie.jpg"
                }
            },
            {
                "id": "prod_grav_lift_003",
                "name": "Grav-Lift Sneakers",
                "description": "Next-gen footwear with simulated weightlessness and dynamic cushioning.",
                "price": 450.00,
                "brand_id": "brand_kinetic_footwear",
                "category": "Shoes",
                "size_chart": {"42": {"length": 27}, "43": {"length": 28}},
                "material": "Nano-Spring Mesh",
                "colors": ["Core White", "Gravity Grey"],
                "dimensions": {"width": 12, "height": 15, "depth": 32},
                "asset_urls": {
                    "3d_model": "/assets/models/grav_lift.glb",
                    "image": "/assets/images/grav_lift.jpg"
                }
            }
        ]

        # 3. Create Products
        for p_data in initial_products:
            db_prod = ProductDB(**p_data)
            db.add(db_prod)
            print(f"✅ Added Product: {p_data['name']}")

        # 4. Create Initial Store
        store_id = "store_flagship_001"
        db_store = StoreDB(
            id=store_id,
            name="AetherStore Flagship",
            brand_id="brand_aether_labs",
            description="The premier showcase for multisensory digital fashion.",
            template="modern_scandinavian",
            products=[p["id"] for p in initial_products],
            settings={
                "vibe": "Luxury Tech-Boutique",
                "lighting": "Cinematic",
                "music_style": "Ambient Deep House"
            },
            is_active=True
        )
        db.add(db_store)
        print(f"✅ Created Flagship Store: {db_store.name}")

        db.commit()
        print("\n✨ Database Seeding Complete. Persistent Collection Ready.")

    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
