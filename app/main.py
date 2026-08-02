from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base, SessionLocal
from . import models, auth
from .routers import auth as auth_router, products, orders, categories, reviews, coupons, blogs, settings, users, dashboard, debug, subscribers
import random
import os

app = FastAPI(
    title="NORV AMS API Gateway",
    description="Backend Node Control REST Services for Atelier Management System (AMS v4.2)",
    version="1.0.0"
)

from fastapi import Request
from fastapi.responses import JSONResponse

# Configure CORS Middleware for cross-origin portals access
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    origin = request.headers.get("origin", "*")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"},
        headers={
            "Access-Control-Allow-Origin": origin if origin else "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# Mount API Routers
app.include_router(auth_router.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(categories.router)
app.include_router(reviews.router)
app.include_router(coupons.router)
app.include_router(blogs.router)
app.include_router(settings.router)
app.include_router(users.router)
app.include_router(dashboard.router)
app.include_router(debug.router)
app.include_router(subscribers.router)


@app.get("/")
def read_root():
    return {
        "status": "online",
        "node": "NORV-MAIN-LHR",
        "version": "AMS v4.2",
        "endpoints_docs": "/docs"
    }

# Database Seeding on Application Startup
@app.on_event("startup")
def startup_db_seeding():
    # 1. Create tables if they do not exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1.5 Auto-migrate missing columns in PostgreSQL database
        from sqlalchemy import text
        alter_queries = [
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS homepage_image VARCHAR;",
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS hover_image VARCHAR;",
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS images JSON;",
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS video_url VARCHAR;",
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS original_price INTEGER;",
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS savings VARCHAR;",
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS badge VARCHAR;",
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS reviews_count INTEGER DEFAULT 0;",
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS rating FLOAT DEFAULT 5.0;",
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS in_stock BOOLEAN DEFAULT TRUE;",
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS key_ingredients JSON;",
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS how_to_use TEXT;",
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS sizes JSON;",
            "ALTER TABLE categories ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'Active';",
            "ALTER TABLE categories ADD COLUMN IF NOT EXISTS products_count INTEGER DEFAULT 0;",
            "ALTER TABLE orders ADD COLUMN IF NOT EXISTS customer_notes TEXT;",
            "ALTER TABLE orders ADD COLUMN IF NOT EXISTS admin_notes TEXT;",
            "ALTER TABLE orders ADD COLUMN IF NOT EXISTS tracking_number VARCHAR DEFAULT 'Not Dispatched';",
            "ALTER TABLE orders ADD COLUMN IF NOT EXISTS estimated_delivery VARCHAR DEFAULT '3-5 Working Days';",
            "ALTER TABLE reviews ADD COLUMN IF NOT EXISTS featured BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE reviews ADD COLUMN IF NOT EXISTS verified BOOLEAN DEFAULT TRUE;",
            "ALTER TABLE reviews ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'Approved';",
            "ALTER TABLE subscribers ADD COLUMN IF NOT EXISTS bundle VARCHAR;",
            "ALTER TABLE subscribers ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'Active';"
        ]
        for query in alter_queries:
            try:
                db.execute(text(query))
            except Exception as ex:
                print(f"Migration notice: {ex}")
        db.commit()

        # 2. Check and clean dummy data
        # If the database contains the dummy product "Acne Control Face Wash" and total products <= 7,
        # we consider it dummy data and wipe it out.
        dummy_check = db.query(models.Product).filter(models.Product.id == 1, models.Product.name == "Acne Control Face Wash").first()
        if dummy_check and db.query(models.Product).count() <= 7:
            db.query(models.Review).delete()
            db.query(models.Order).delete()
            db.query(models.Coupon).delete()
            db.query(models.BlogArticle).delete()
            db.query(models.Product).delete()
            db.query(models.Category).delete()
            db.commit()
            print("Successfully wiped dummy data from the database.")

        # 3. Seed Default Admin Users
        user_shopnorv = db.query(models.AdminUser).filter(models.AdminUser.email == "shopnorv@gmail.com").first()
        if not user_shopnorv:
            user_shopnorv = models.AdminUser(
                name="NORV Super Admin",
                email="shopnorv@gmail.com",
                hashed_password=auth.get_password_hash("Norv786$$"),
                role="Super Admin",
                status="Active",
                last_active="Never",
                avatar="https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=150&auto=format&fit=crop"
            )
            db.add(user_shopnorv)
            db.commit()
            print("Successfully seeded shopnorv@gmail.com.")
        else:
            user_shopnorv.hashed_password = auth.get_password_hash("Norv786$$")
            user_shopnorv.role = "Super Admin"
            user_shopnorv.status = "Active"
            db.commit()
            print("Successfully updated shopnorv@gmail.com password.")

        if db.query(models.AdminUser).count() == 0:
            superadmin = models.AdminUser(
                name="Ali Khubaib (You)",
                email="alikhubaib959@gmail.com",
                hashed_password=auth.get_password_hash("norv2026"),
                role="Super Admin",
                status="Active",
                last_active="Never",
                avatar="https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=150&auto=format&fit=crop"
            )
            # Add secondary fallback Super Admin
            superadmin_alt = models.AdminUser(
                name="Super Admin Node",
                email="superadmin@norv.pk",
                hashed_password=auth.get_password_hash("norv2026"),
                role="Super Admin",
                status="Active",
                last_active="Never",
                avatar="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?q=80&w=150&auto=format&fit=crop"
            )
            standard_admin = models.AdminUser(
                name="Bilal Khan",
                email="admin@norv.pk",
                hashed_password=auth.get_password_hash("norv2026"),
                role="Admin",
                status="Active",
                last_active="Never",
                avatar="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=150&auto=format&fit=crop"
            )
            db.add_all([superadmin, superadmin_alt, standard_admin])
            db.commit()
            print("Successfully seeded legacy Admin Users.")

        # 4. Seed Default Store Settings
        if db.query(models.StoreSettings).count() == 0:
            store_settings = models.StoreSettings(
                id=1,
                store_name="NORV Men's Grooming",
                business_email="info@norv.pk",
                support_phone="+92 300 1234567",
                address="Building 45-B, Sector Z, Phase III, DHA, Lahore, Pakistan",
                currency="PKR",
                shipping_charges_cod=250,
                shipping_charges_card=150,
                free_shipping_threshold=3500,
                tax_rate_percent=16.0,
                is_maintenance_mode=False,
                low_stock_alert_threshold=10
            )
            db.add(store_settings)
            db.commit()
            print("Successfully seeded Store Settings.")

        # 5. Synchronize PostgreSQL serial sequences to prevent duplicate key violations
        from sqlalchemy import text
        bind_engine = db.get_bind()
        if "postgresql" in bind_engine.driver:
            tables = ["categories", "products", "reviews", "coupons", "blog_articles", "admin_users"]
            for table in tables:
                db.execute(text(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM {table};"))
            db.commit()
            print("Successfully synchronized PostgreSQL sequences.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

