from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base, SessionLocal
from . import models, auth
from .routers import auth as auth_router, products, orders, categories, reviews, coupons, blogs, settings, users
import random
import os

app = FastAPI(
    title="NORV AMS API Gateway",
    description="Backend Node Control REST Services for Atelier Management System (AMS v4.2)",
    version="1.0.0"
)

# Configure CORS Middleware for cross-origin portals access
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "https://norv-grooming.vercel.app",
    "https://admin-norv.vercel.app",
    "https://norvfe-9s7v.vercel.app",
    "https://norvfe.vercel.app",
]

# Allow additional origins from environment variables if set
env_origins = os.getenv("ALLOWED_ORIGINS")
if env_origins:
    allowed_origins.extend([o.strip() for o in env_origins.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        # 2. Seed Default Admin Users
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

        # 3. Seed Default Store Settings
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

        # 4. Seed Default Categories
        if db.query(models.Category).count() == 0:
            categories_list = [
                models.Category(id=1, name="Skincare", slug="skincare", image="https://images.unsplash.com/photo-1556228720-195a672e8a03?q=80&w=600&auto=format&fit=crop", status="Active", products_count=4),
                models.Category(id=2, name="Hair Care", slug="hair-care", image="https://images.unsplash.com/photo-1620916566398-39f1143ab7be?q=80&w=600&auto=format&fit=crop", status="Active", products_count=1),
                models.Category(id=3, name="Beard Care", slug="beard-care", image="https://images.unsplash.com/photo-1540555700478-4be289fbecef?q=80&w=600&auto=format&fit=crop", status="Active", products_count=1),
                models.Category(id=4, name="Fragrance", slug="fragrance", image="https://images.unsplash.com/photo-1547887537-6158d64c35b3?q=80&w=600&auto=format&fit=crop", status="Active", products_count=1),
                models.Category(id=5, name="Bundles", slug="bundles", image="https://images.unsplash.com/photo-1503951914875-452162b0f3f1?q=80&w=600&auto=format&fit=crop", status="Active", products_count=1)
            ]
            db.add_all(categories_list)
            db.commit()
            print("Successfully seeded Categories.")

        # 5. Seed Default Products
        if db.query(models.Product).count() == 0:
            products_list = [
                models.Product(
                    id=1, name="Acne Control Face Wash", price=1299, original_price=1620, savings="Save Rs. 321", badge="Clinical Cleanse",
                    sizes=["100 ML"], rating=4.8, reviews_count=142, in_stock=True, category="Skincare",
                    description="Deep-cleansing gel that eliminates acne-causing bacteria, unclogs pores, and prevents future breakouts.",
                    key_ingredients=["Salicylic Acid 1%", "Tea Tree Oil extract", "Charcoal Powder", "Organic Aloe Vera extract"],
                    how_to_use="Morning & Night: Apply a small amount to wet face. Gently massage for 60 seconds, then rinse.",
                    image="https://images.unsplash.com/photo-1556228720-195a672e8a03?q=80&w=600&auto=format&fit=crop",
                    images=[
                        "https://images.unsplash.com/photo-1556228720-195a672e8a03?q=80&w=600&auto=format&fit=crop",
                        "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?q=80&w=600&auto=format&fit=crop",
                        "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?q=80&w=600&auto=format&fit=crop"
                    ]
                ),
                models.Product(
                    id=2, name="Oil Control Face Wash", price=1199, original_price=1499, savings="Save Rs. 300", badge="12h Oil-Free",
                    sizes=["100 ML"], rating=4.7, reviews_count=118, in_stock=True, category="Skincare",
                    description="Powerful sebum-regulating cleanser for men with oily, shiny skin. Controls excess oil for up to 12 hours.",
                    key_ingredients=["Witch Hazel Extract", "Niacinamide 2%", "Charcoal Extract", "Pure Zinc PCA"],
                    how_to_use="Morning & Night: Squeeze a pea-sized amount onto wet palms, lather well, massage gently, and rinse off.",
                    image="https://images.unsplash.com/photo-1620916566398-39f1143ab7be?q=80&w=600&auto=format&fit=crop",
                    images=[
                        "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?q=80&w=600&auto=format&fit=crop",
                        "https://images.unsplash.com/photo-1556228720-195a672e8a03?q=80&w=600&auto=format&fit=crop",
                        "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?q=80&w=600&auto=format&fit=crop"
                    ]
                ),
                models.Product(
                    id=3, name="Deep Exfoliating Face Scrub", price=999, original_price=1250, savings="Save Rs. 251", badge="Blackhead Cleanse",
                    sizes=["75 ML"], rating=4.9, reviews_count=184, in_stock=True, category="Skincare",
                    description="Manual exfoliant for men's thicker skin. Removes dead cells, unclogs pores, and eliminates blackheads.",
                    key_ingredients=["Crushed Apricot Kernel Shells", "Organic Volcanic Sand", "Pure Menthol Crystals", "Squalane"],
                    how_to_use="Use 2-3 times per week: Rub a hazelnut-sized amount onto wet face, focusing especially on nose/chin. Rinse.",
                    image="https://images.unsplash.com/photo-1503951914875-452162b0f3f1?q=80&w=600&auto=format&fit=crop",
                    images=[
                        "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?q=80&w=600&auto=format&fit=crop",
                        "https://images.unsplash.com/photo-1556228720-195a672e8a03?q=80&w=600&auto=format&fit=crop",
                        "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?q=80&w=600&auto=format&fit=crop"
                    ]
                ),
                models.Product(
                    id=4, name="Daily Defense Moisturiser", price=1499, original_price=1875, savings="Save Rs. 376", badge="Barrier Defense",
                    sizes=["50 ML"], rating=4.7, reviews_count=96, in_stock=True, category="Skincare",
                    description="Lightweight oil-free moisturiser built for men. Hydrates deeply without greasiness and strengthens skin barrier.",
                    key_ingredients=["Ceramide NP", "Hyaluronic Acid 2%", "Squalane oil", "Organic Shea Butter extract"],
                    how_to_use="Apply to clean, dry face morning or evening. Smooth gently into skin until fully absorbed.",
                    image="https://images.unsplash.com/photo-1601049541289-9b1b7bbbfe19?q=80&w=600&auto=format&fit=crop",
                    images=[
                        "https://images.unsplash.com/photo-1601049541289-9b1b7bbbfe19?q=80&w=600&auto=format&fit=crop",
                        "https://images.unsplash.com/photo-1617897903246-719242758050?q=80&w=600&auto=format&fit=crop",
                        "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?q=80&w=600&auto=format&fit=crop"
                    ]
                ),
                models.Product(
                    id=5, name="Beard Growth Serum", price=2299, original_price=2875, savings="Save Rs. 576", badge="Follicle Stimulating",
                    sizes=["30 ML"], rating=4.8, reviews_count=75, in_stock=True, category="Beard Care",
                    description="Concentrated treatment serum targeting beard density and strength. Stimulates follicles over 4-6 weeks.",
                    key_ingredients=["Biotin complex", "Rosemary Essential Oil", "Castor Oil extract", "Hydrolyzed Keratin Protein"],
                    how_to_use="Apply 3-4 drops directly to clean skin under beard. Massage thoroughly. Use daily.",
                    image="https://images.unsplash.com/photo-1540555700478-4be289fbecef?q=80&w=600&auto=format&fit=crop",
                    images=[
                        "https://images.unsplash.com/photo-1540555700478-4be289fbecef?q=80&w=600&auto=format&fit=crop",
                        "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?q=80&w=600&auto=format&fit=crop",
                        "https://images.unsplash.com/photo-1556228720-195a672e8a03?q=80&w=600&auto=format&fit=crop"
                    ]
                ),
                models.Product(
                    id=6, name="Hair Strengthening Serum", price=2499, original_price=3125, savings="Save Rs. 626", badge="Root Recovery",
                    sizes=["50 ML"], rating=4.6, reviews_count=68, in_stock=True, category="Hair Care",
                    description="Leave-in treatment for scalp and hair. Targets hair fall, weak roots, and damaged hair shaft.",
                    key_ingredients=["Redensyl active formula", "Onion Extract", "Niacinamide 5%", "Vitamin E active"],
                    how_to_use="Apply a few drops onto scalp or towel-dried hair after washing. Massage gently. Leave in.",
                    image="https://images.unsplash.com/photo-1620916566398-39f1143ab7be?q=80&w=600&auto=format&fit=crop",
                    images=[
                        "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?q=80&w=600&auto=format&fit=crop",
                        "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?q=80&w=600&auto=format&fit=crop",
                        "https://images.unsplash.com/photo-1540555700478-4be289fbecef?q=80&w=600&auto=format&fit=crop"
                    ]
                ),
                models.Product(
                    id=7, name="Woody Oud Mist", price=2999, original_price=3750, savings="Save Rs. 751", badge="Signature Scent",
                    sizes=["100 ML"], rating=4.9, reviews_count=154, in_stock=True, category="Fragrance",
                    description="A rich, sophisticated blend of Cambodian Oud, cedarwood, and amber. Formulated for long-lasting presence.",
                    key_ingredients=["Cambodian Oud Extract", "Cedarwood Oil", "Amber Accord", "Bergamot Essence"],
                    how_to_use="Spray onto pulse points from a distance of 6 inches. Allow to dry naturally without rubbing.",
                    image="https://images.unsplash.com/photo-1547887537-6158d64c35b3?q=80&w=600&auto=format&fit=crop",
                    images=[
                        "https://images.unsplash.com/photo-1547887537-6158d64c35b3?q=80&w=600&auto=format&fit=crop",
                        "https://images.unsplash.com/photo-1601049541289-9b1b7bbbfe19?q=80&w=600&auto=format&fit=crop",
                        "https://images.unsplash.com/photo-1617897903246-719242758050?q=80&w=600&auto=format&fit=crop"
                    ]
                )
            ]
            db.add_all(products_list)
            db.commit()
            print("Successfully seeded Products.")

        # 6. Seed Default Reviews
        if db.query(models.Review).count() == 0:
            reviews_list = [
                models.Review(product_name="Acne Control Face Wash", reviewer_name="Bilal K.", location="Lahore", rating=5, text="The salicylic acid concentration seems perfect. Cleansed deep down and does not strip my oily skin dry at all.", date="June 01, 2026", status="Approved", featured=True, verified=True),
                models.Review(product_name="Beard Growth Serum", reviewer_name="Kamran Shah", location="Karachi", rating=4, text="Seeing noticeable patch fill-ins on cheeks after 4 weeks. Great product.", date="June 03, 2026", status="Approved", featured=False, verified=True),
                models.Review(product_name="Oil Control Face Wash", reviewer_name="Farhan A.", location="Rawalpindi", rating=2, text="Scent is nice, but it was slightly irritating around eye area.", date="June 04, 2026", status="Pending", featured=False, verified=False)
            ]
            db.add_all(reviews_list)
            db.commit()
            print("Successfully seeded Reviews.")

        # 7. Seed Default Coupons
        if db.query(models.Coupon).count() == 0:
            coupons_list = [
                models.Coupon(code="NORVSAIL", type="Percentage", value=15.0, start_date="2026-06-01", end_date="2026-07-31", usage_limit=500, usage_count=142, status="Active"),
                models.Coupon(code="LUXURY500", type="Fixed Amount", value=500.0, start_date="2026-06-05", end_date="2026-06-30", usage_limit=200, usage_count=48, status="Active"),
                models.Coupon(code="WELCOME10", type="Percentage", value=10.0, start_date="2026-01-01", end_date="2026-12-31", usage_limit=9999, usage_count=1204, status="Active")
            ]
            db.add_all(coupons_list)
            db.commit()
            print("Successfully seeded Coupons.")

        # 8. Seed Default Blogs
        if db.query(models.BlogArticle).count() == 0:
            blogs_list = [
                models.BlogArticle(
                    title="The Science of Skin Barrier Repair", slug="science-skin-barrier-repair", category="Skincare Science",
                    read_time="4 min read", excerpt="Learn why your skin barrier is your most important defense system and how NORV formulations strengthen it.",
                    content="The skin barrier is your body's shield against dry dust, Lahore smog, and Karachi salt breezes. When compromised by harsh chemical detergents, skin undergoes micro-tearing.",
                    date="2026-06-01", image="https://images.unsplash.com/photo-1512290923902-8a9f81dc236c?q=80&w=600&auto=format&fit=crop",
                    status="Published", publish_date="2026-06-01", seo_title="Skin Barrier Repair: Skincare Science for Men", seo_description="Unpack the biological mechanics of the male stratum corneum."
                ),
                models.BlogArticle(
                    title="Building Your Morning Grooming Ritual", slug="building-morning-grooming-ritual", category="Lifestyle",
                    read_time="5 min read", excerpt="The first 15 minutes of your morning define your entire day. Here's how to build a premium ritual.",
                    content="Successful men do not stumble into their day; they arrive with distinct, focused presence. Self-care is a fundamental tenet of personal discipline.",
                    date="2026-05-20", image="https://images.unsplash.com/photo-1503951914875-452162b0f3f1?q=80&w=600&auto=format&fit=crop",
                    status="Published", publish_date="2026-05-20", seo_title="Men's Morning Grooming Routine Guide", seo_description="A premium 15-minute sequence for the modern elite gentleman."
                )
            ]
            db.add_all(blogs_list)
            db.commit()
            print("Successfully seeded Blog Articles.")

        # 9. Seed Default Orders
        if db.query(models.Order).count() == 0:
            orders_list = [
                models.Order(
                    id="NRV-918341", name="Bilal K.", email="bilal.lhr@gmail.com", phone="+92 300 1234567",
                    address="Phase 5, DHA, Block CCA, House 14", city="Lahore", payment_method="COD",
                    items=[
                        {"productId": 1, "name": "Acne Control Face Wash", "quantity": 1, "size": "100 ML", "price": 1299},
                        {"productId": 4, "name": "Daily Defense Moisturiser", "quantity": 1, "size": "50 ML", "price": 1499}
                    ],
                    total=3048, status="Delivered", date="June 01, 2026 10:30 AM", estimated_delivery="June 04, 2026",
                    tracking_number="PK-4183421-LX", customer_notes="Please deliver after 2:00 PM.", admin_notes="Client verified, delivery successful."
                ),
                models.Order(
                    id="NRV-382910", name="Kamran Shah", email="shah.khi@gmail.com", phone="+92 321 9876543",
                    address="Apartment 4B, Creek Vista, Phase 8, DHA", city="Karachi", payment_method="Card",
                    items=[
                        {"productId": 5, "name": "Beard Growth Serum", "quantity": 2, "size": "30 ML", "price": 2299}
                    ],
                    total=4598, status="Shipped", date="June 05, 2026 04:15 PM", estimated_delivery="June 09, 2026",
                    tracking_number="PK-8291024-LX", customer_notes="Please ring doorbell or call.", admin_notes="Card payment processed. Dispensed."
                )
            ]
            db.add_all(orders_list)
            db.commit()
            print("Successfully seeded Orders.")

        # 10. Synchronize PostgreSQL serial sequences to prevent duplicate key violations
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
