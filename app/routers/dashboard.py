from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, auth

router = APIRouter(
    prefix="/api/dashboard",
    tags=["dashboard"]
)

@router.get("/stats")
def get_dashboard_stats(
    current_user: models.AdminUser = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # Fetch all orders to compute stats
    orders = db.query(models.Order).all()
    total_revenue = sum(order.total for order in orders)
    total_orders = len(orders)
    
    # Extract unique customer emails
    unique_customers = len(set(order.email.lower() for order in orders if order.email))
    
    # Count pending and completed orders
    pending_orders_count = sum(1 for o in orders if o.status in ["Processing", "Shipped", "Out for Delivery"])
    delivered_orders_count = sum(1 for o in orders if o.status == "Delivered")
    
    # Fetch product and category counts
    products_count = db.query(models.Product).count()
    categories_count = db.query(models.Category).count()
    
    # Count products out of stock
    low_stock_count = db.query(models.Product).filter(models.Product.in_stock == False).count()
    
    # Aggregate monthly revenue for the charts
    monthly_sales = {
        "Jan": 0, "Feb": 0, "Mar": 0, "Apr": 0, "May": 0, "Jun": 0,
        "Jul": 0, "Aug": 0, "Sep": 0, "Oct": 0, "Nov": 0, "Dec": 0
    }
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    months_full = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    
    for order in orders:
        order_month = None
        if order.date:
            for i, m_name in enumerate(months_full):
                if m_name in order.date:
                    order_month = month_names[i]
                    break
            if not order_month:
                for m_short in month_names:
                    if m_short in order.date:
                        order_month = m_short
                        break
        # Fallback default if not parsed
        if not order_month:
            order_month = "Jun"
            
        monthly_sales[order_month] += order.total
        
    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_customers": unique_customers,
        "pending_orders": pending_orders_count,
        "completed_orders": delivered_orders_count,
        "products_count": products_count,
        "categories_count": categories_count,
        "low_stock_count": low_stock_count,
        "monthly_sales": [
            {"month": m, "amount": monthly_sales[m]} for m in month_names
        ]
    }
