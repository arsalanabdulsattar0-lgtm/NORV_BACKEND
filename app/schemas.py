from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    name: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class LoginRequest(BaseModel):
    username: str  # email or username
    password: str

# Admin User Schemas
class AdminUserBase(BaseModel):
    name: str
    email: EmailStr
    role: str
    status: str
    avatar: Optional[str] = None

class AdminUserCreate(AdminUserBase):
    password: str

class AdminUserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    status: Optional[str] = None
    avatar: Optional[str] = None
    password: Optional[str] = None

class AdminUserOut(AdminUserBase):
    id: int
    last_active: Optional[str] = None

    class Config:
        from_attributes = True

# Product Schemas
class ProductBase(BaseModel):
    name: Optional[str] = "Unnamed Product"
    price: Optional[int] = 0
    original_price: Optional[int] = None
    savings: Optional[str] = None
    badge: Optional[str] = None
    sizes: Optional[List[str]] = []
    rating: Optional[float] = 5.0
    reviews_count: Optional[int] = 0
    in_stock: Optional[bool] = True
    category: Optional[str] = "Grooming"
    description: Optional[str] = ""
    key_ingredients: Optional[List[str]] = []
    how_to_use: Optional[str] = ""
    image: Optional[str] = ""
    homepage_image: Optional[str] = None
    hover_image: Optional[str] = None
    images: Optional[List[str]] = None
    video_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int

    class Config:
        from_attributes = True

# Category Schemas
class CategoryBase(BaseModel):
    name: Optional[str] = ""
    slug: Optional[str] = ""
    image: Optional[str] = ""
    status: Optional[str] = "Active"
    products_count: Optional[int] = 0

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int

    class Config:
        from_attributes = True

# Order Schemas
class OrderItem(BaseModel):
    productId: Optional[int] = 0
    name: Optional[str] = ""
    quantity: Optional[int] = 1
    size: Optional[str] = ""
    price: Optional[int] = 0

class OrderBase(BaseModel):
    name: Optional[str] = "Client"
    email: Optional[str] = ""
    phone: Optional[str] = ""
    address: Optional[str] = ""
    city: Optional[str] = ""
    payment_method: Optional[str] = "COD"
    items: Optional[List[Any]] = []
    total: Optional[int] = 0
    status: Optional[str] = "Processing"
    estimated_delivery: Optional[str] = "3-5 Working Days"
    tracking_number: Optional[str] = "Not Dispatched"
    customer_notes: Optional[str] = ""
    admin_notes: Optional[str] = ""

class OrderCreate(OrderBase):
    id: Optional[str] = None  # Admin can specify ID or let it auto-generate

class OrderUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    payment_method: Optional[str] = None
    items: Optional[List[Any]] = None
    total: Optional[int] = None
    status: Optional[str] = None
    estimated_delivery: Optional[str] = None
    tracking_number: Optional[str] = None
    customer_notes: Optional[str] = None
    admin_notes: Optional[str] = None

class OrderOut(OrderBase):
    id: str
    date: str

    class Config:
        from_attributes = True

# Review Schemas
class ReviewBase(BaseModel):
    product_name: str
    reviewer_name: str
    location: str
    rating: int
    text: str
    date: str
    status: Optional[str] = "Pending"
    featured: Optional[bool] = False
    verified: Optional[bool] = True

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    status: Optional[str] = None
    featured: Optional[bool] = None

class ReviewOut(ReviewBase):
    id: int

    class Config:
        from_attributes = True

# Coupon Schemas
class CouponBase(BaseModel):
    code: str
    type: str
    value: float
    start_date: str
    end_date: str
    usage_limit: int
    usage_count: Optional[int] = 0
    status: Optional[str] = "Active"

class CouponCreate(CouponBase):
    pass

class CouponOut(CouponBase):
    id: int

    class Config:
        from_attributes = True

# BlogArticle Schemas
class BlogArticleBase(BaseModel):
    title: str
    slug: str
    category: str
    read_time: str
    excerpt: str
    content: str
    date: str
    image: str
    status: Optional[str] = "Published"
    publish_date: str
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None

class BlogArticleCreate(BlogArticleBase):
    pass

class BlogArticleOut(BlogArticleBase):
    id: int

    class Config:
        from_attributes = True

# StoreSettings Schemas
class StoreSettingsBase(BaseModel):
    store_name: str
    business_email: str
    support_phone: str
    address: str
    currency: Optional[str] = "PKR"
    shipping_charges_cod: Optional[int] = 250
    shipping_charges_card: Optional[int] = 150
    free_shipping_threshold: Optional[int] = 3500
    tax_rate_percent: Optional[float] = 16.0
    is_maintenance_mode: Optional[bool] = False
    low_stock_alert_threshold: Optional[int] = 10

class StoreSettingsCreate(StoreSettingsBase):
    pass

class StoreSettingsOut(StoreSettingsBase):
    id: int

    class Config:
        from_attributes = True

# Subscriber Schemas
class SubscriberCreate(BaseModel):
    email: EmailStr
    bundle: Optional[str] = None

class SubscriberUpdate(BaseModel):
    status: Optional[str] = None

class SubscriberOut(BaseModel):
    id: int
    email: str
    bundle: Optional[str] = None
    timestamp: str
    status: str

    class Config:
        from_attributes = True
