from sqlalchemy.orm import Session
from . import models, schemas, auth
from datetime import datetime

# ==================== ADMIN USERS CRUD ====================
def get_admin_user_by_email(db: Session, email: str):
    return db.query(models.AdminUser).filter(models.AdminUser.email == email).first()

def get_admin_users(db: Session):
    return db.query(models.AdminUser).all()

def create_admin_user(db: Session, user: schemas.AdminUserCreate):
    hashed_pwd = auth.get_password_hash(user.password)
    db_user = models.AdminUser(
        name=user.name,
        email=user.email,
        hashed_password=hashed_pwd,
        role=user.role,
        status=user.status,
        avatar=user.avatar,
        last_active="Never"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_admin_user(db: Session, user_id: int, user_update: schemas.AdminUserUpdate):
    db_user = db.query(models.AdminUser).filter(models.AdminUser.id == user_id).first()
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        db_user.hashed_password = auth.get_password_hash(update_data["password"])
        del update_data["password"]
        
    for key, val in update_data.items():
        setattr(db_user, key, val)
        
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_admin_user(db: Session, user_id: int):
    db_user = db.query(models.AdminUser).filter(models.AdminUser.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

# ==================== PRODUCTS CRUD ====================
def get_products(db: Session):
    return db.query(models.Product).order_by(models.Product.id.desc()).all()

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: int, product_update: schemas.ProductCreate):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        return None
    for key, val in product_update.dict().items():
        setattr(db_product, key, val)
    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    try:
        db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if db_product:
            db.delete(db_product)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"Error deleting product {product_id}: {e}")
        return False

# ==================== CATEGORIES CRUD ====================
def get_categories(db: Session):
    return db.query(models.Category).all()

def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def update_category(db: Session, cat_id: int, category_update: schemas.CategoryCreate):
    db_category = db.query(models.Category).filter(models.Category.id == cat_id).first()
    if not db_category:
        return None
    for key, val in category_update.dict().items():
        setattr(db_category, key, val)
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, cat_id: int):
    db_category = db.query(models.Category).filter(models.Category.id == cat_id).first()
    if db_category:
        db.delete(db_category)
        db.commit()
        return True
    return False

# ==================== ORDERS CRUD ====================
def get_orders(db: Session):
    return db.query(models.Order).order_by(models.Order.date.desc()).all()

def get_order(db: Session, order_id: str):
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def create_order(db: Session, order: schemas.OrderCreate):
    order_data = order.model_dump()
    if not order_data.get("id"):
        import random
        order_data["id"] = f"NRV-{random.randint(100000, 999999)}"
        
    order_data["date"] = datetime.now().strftime("%B %d, %Y %I:%M %p")
    # Safely serialize items — they may already be dicts or Pydantic models
    serialized_items = []
    for item in order_data.get("items", []):
        if isinstance(item, dict):
            serialized_items.append(item)
        else:
            serialized_items.append(item.dict())
    order_data["items"] = serialized_items
    
    db_order = models.Order(**order_data)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def update_order(db: Session, order_id: str, order_update: schemas.OrderUpdate):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        return None
    
    update_data = order_update.model_dump(exclude_unset=True)
    if "items" in update_data and update_data["items"]:
        serialized = []
        for item in update_data["items"]:
            if isinstance(item, dict):
                serialized.append(item)
            else:
                serialized.append(item.dict())
        update_data["items"] = serialized
        
    for key, val in update_data.items():
        setattr(db_order, key, val)
        
    db.commit()
    db.refresh(db_order)
    return db_order

def delete_order(db: Session, order_id: str):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order:
        db.delete(db_order)
        db.commit()
        return True
    return False

# ==================== REVIEWS CRUD ====================
def get_reviews(db: Session):
    return db.query(models.Review).order_by(models.Review.id.desc()).all()

def create_review(db: Session, review: schemas.ReviewCreate):
    db_review = models.Review(**review.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def update_review(db: Session, review_id: int, review_update: schemas.ReviewUpdate):
    db_review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not db_review:
        return None
    for key, val in review_update.dict(exclude_unset=True).items():
        setattr(db_review, key, val)
    db.commit()
    db.refresh(db_review)
    return db_review

def delete_review(db: Session, review_id: int):
    db_review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if db_review:
        db.delete(db_review)
        db.commit()
        return True
    return False

# ==================== COUPONS CRUD ====================
def get_coupons(db: Session):
    return db.query(models.Coupon).all()

def create_coupon(db: Session, coupon: schemas.CouponCreate):
    db_coupon = models.Coupon(**coupon.dict())
    db.add(db_coupon)
    db.commit()
    db.refresh(db_coupon)
    return db_coupon

def update_coupon(db: Session, coupon_id: int, coupon_update: schemas.CouponCreate):
    db_coupon = db.query(models.Coupon).filter(models.Coupon.id == coupon_id).first()
    if not db_coupon:
        return None
    for key, val in coupon_update.dict().items():
        setattr(db_coupon, key, val)
    db.commit()
    db.refresh(db_coupon)
    return db_coupon

def delete_coupon(db: Session, coupon_id: int):
    db_coupon = db.query(models.Coupon).filter(models.Coupon.id == coupon_id).first()
    if db_coupon:
        db.delete(db_coupon)
        db.commit()
        return True
    return False

# ==================== BLOGS CRUD ====================
def get_blogs(db: Session):
    return db.query(models.BlogArticle).order_by(models.BlogArticle.id.desc()).all()

def create_blog(db: Session, blog: schemas.BlogArticleCreate):
    db_blog = models.BlogArticle(**blog.dict())
    db.add(db_blog)
    db.commit()
    db.refresh(db_blog)
    return db_blog

def update_blog(db: Session, blog_id: int, blog_update: schemas.BlogArticleCreate):
    db_blog = db.query(models.BlogArticle).filter(models.BlogArticle.id == blog_id).first()
    if not db_blog:
        return None
    for key, val in blog_update.dict().items():
        setattr(db_blog, key, val)
    db.commit()
    db.refresh(db_blog)
    return db_blog

def delete_blog(db: Session, blog_id: int):
    db_blog = db.query(models.BlogArticle).filter(models.BlogArticle.id == blog_id).first()
    if db_blog:
        db.delete(db_blog)
        db.commit()
        return True
    return False

# ==================== SETTINGS CRUD ====================
def get_settings(db: Session):
    # Retrieve single settings record (ID=1)
    db_settings = db.query(models.StoreSettings).filter(models.StoreSettings.id == 1).first()
    if not db_settings:
        db_settings = models.StoreSettings(
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
        db.add(db_settings)
        db.commit()
        db.refresh(db_settings)
    return db_settings

def update_settings(db: Session, settings_update: schemas.StoreSettingsBase):
    db_settings = get_settings(db)
    for key, val in settings_update.dict().items():
        setattr(db_settings, key, val)
    db.commit()
    db.refresh(db_settings)
    return db_settings
