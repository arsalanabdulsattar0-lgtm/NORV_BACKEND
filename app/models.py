from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, Text, DateTime
import datetime
from .database import Base

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="Admin")  # "Super Admin" or "Admin"
    status = Column(String, default="Active")  # "Active" or "Suspended"
    last_active = Column(String, nullable=True)
    avatar = Column(String, nullable=True)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    original_price = Column(Integer, nullable=True)
    savings = Column(String, nullable=True)
    badge = Column(String, nullable=True)
    sizes = Column(JSON, nullable=False)  # list of strings
    rating = Column(Float, default=5.0)
    reviews_count = Column(Integer, default=0)
    in_stock = Column(Boolean, default=True)
    category = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    key_ingredients = Column(JSON, nullable=False)  # list of strings
    how_to_use = Column(Text, nullable=False)
    image = Column(String, nullable=False)
    homepage_image = Column(String, nullable=True)
    hover_image = Column(String, nullable=True)
    images = Column(JSON, nullable=True)  # list of image URLs
    video_url = Column(String, nullable=True)

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    image = Column(String, nullable=False)
    status = Column(String, default="Active")  # "Active" or "Draft"
    products_count = Column(Integer, default=0)

class Order(Base):
    __tablename__ = "orders"

    # Order ID is generated manually like NRV-102948
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    address = Column(Text, nullable=False)
    city = Column(String, nullable=False)
    payment_method = Column(String, nullable=False)  # "COD" or "Card"
    items = Column(JSON, nullable=False)  # list of dicts: {productId, name, quantity, size, price}
    total = Column(Integer, nullable=False)
    status = Column(String, default="Processing")  # "Processing", "Shipped", "Out for Delivery", "Delivered"
    date = Column(String, nullable=False)
    estimated_delivery = Column(String, nullable=False)
    tracking_number = Column(String, default="Not Dispatched")
    customer_notes = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, nullable=False)
    reviewer_name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    date = Column(String, nullable=False)
    status = Column(String, default="Pending")  # "Approved", "Pending", "Rejected"
    featured = Column(Boolean, default=False)
    verified = Column(Boolean, default=True)

class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    type = Column(String, nullable=False)  # "Percentage", "Fixed Amount", "Free Shipping"
    value = Column(Float, nullable=False)
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)
    usage_limit = Column(Integer, nullable=False)
    usage_count = Column(Integer, default=0)
    status = Column(String, default="Active")  # "Active" or "Expired"

class BlogArticle(Base):
    __tablename__ = "blog_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, nullable=False)
    read_time = Column(String, nullable=False)
    excerpt = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    date = Column(String, nullable=False)
    image = Column(String, nullable=False)
    status = Column(String, default="Published")  # "Published", "Scheduled", "Draft"
    publish_date = Column(String, nullable=False)
    seo_title = Column(String, nullable=True)
    seo_description = Column(Text, nullable=True)

class StoreSettings(Base):
    __tablename__ = "store_settings"

    id = Column(Integer, primary_key=True, default=1)
    store_name = Column(String, nullable=False)
    business_email = Column(String, nullable=False)
    support_phone = Column(String, nullable=False)
    address = Column(Text, nullable=False)
    currency = Column(String, default="PKR")
    shipping_charges_cod = Column(Integer, default=250)
    shipping_charges_card = Column(Integer, default=150)
    free_shipping_threshold = Column(Integer, default=3500)
    tax_rate_percent = Column(Float, default=16.0)
    is_maintenance_mode = Column(Boolean, default=False)
    low_stock_alert_threshold = Column(Integer, default=10)

class Subscriber(Base):
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    bundle = Column(String, nullable=True)  # Which bundle they signed up for
    timestamp = Column(String, nullable=False)  # ISO string timestamp
    status = Column(String, default="Active")  # "Active" or "Unsubscribed"
