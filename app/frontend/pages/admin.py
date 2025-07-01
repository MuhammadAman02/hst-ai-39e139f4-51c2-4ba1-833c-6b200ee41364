"""Admin panel for store management."""

from nicegui import ui
from app.frontend.components.layout import page_layout
from app.services.product_service import ProductService
from app.services.category_service import CategoryService
from app.services.order_service import OrderService
from app.services.user_service import UserService
from app.core.database import Session, engine
from app.core.auth import AuthManager, require_admin
from app.models.order import OrderStatus

@ui.page('/admin')
@require_admin
def admin_page():
    """Admin dashboard."""
    
    def admin_content():
        ui.label('Admin Dashboard').classes('text-3xl font-bold mb-8 text-center')
        
        # Admin navigation tabs
        with ui.tabs().classes('w-full') as tabs:
            products_tab = ui.tab('Products')
            orders_tab = ui.tab('Orders')
            users_tab = ui.tab('Users')
            analytics_tab = ui.tab('Analytics')
        
        with ui.tab_panels(tabs, value=products_tab).classes('w-full'):
            # Products management
            with ui.tab_panel(products_tab):
                products_management()
            
            # Orders management
            with ui.tab_panel(orders_tab):
                orders_management()
            
            # Users management
            with ui.tab_panel(users_tab):
                users_management()
            
            # Analytics
            with ui.tab_panel(analytics_tab):
                analytics_dashboard()
    
    def products_management():
        """Products management interface."""
        ui.label('Products Management').classes('text-2xl font-bold mb-6')
        
        with ui.row().classes('w-full justify-between mb-6'):
            ui.button('Add New Product', on_click=lambda: show_add_product_dialog()).classes('luxury-button')
            ui.button('Refresh', on_click=lambda: load_products()).classes('border border-gray-400')
        
        products_container = ui.column().classes('w-full')
        
        def load_products():
            """Load and display products."""
            products_container.clear()
            
            try:
                with Session(engine) as db:
                    product_service = ProductService(db)
                    products = product_service.get_products(limit=100)
                    
                    with products_container:
                        if products:
                            with ui.table(columns=[
                                {'name': 'id', 'label': 'ID', 'field': 'id'},
                                {'name': 'name', 'label': 'Name', 'field': 'name'},
                                {'name': 'category', 'label': 'Category', 'field': 'category'},
                                {'name': 'price', 'label': 'Price', 'field': 'price'},
                                {'name': 'stock', 'label': 'Stock', 'field': 'stock'},
                                {'name': 'status', 'label': 'Status', 'field': 'status'},
                                {'name': 'actions', 'label': 'Actions', 'field': 'actions'}
                            ]).classes('w-full') as table:
                                
                                for product in products:
                                    table.add_row({
                                        'id': product.id,
                                        'name': product.name,
                                        'category': product.category.name,
                                        'price': f'${product.price:.2f}',
                                        'stock': product.stock_quantity,
                                        'status': 'Active' if product.is_active else 'Inactive',
                                        'actions': f'Edit | Delete'
                                    })
                        else:
                            ui.label('No products found').classes('text-gray-500')
            
            except Exception as e:
                with products_container:
                    ui.label(f'Error loading products: {str(e)}').classes('text-red-500')
        
        def show_add_product_dialog():
            """Show add product dialog."""
            with ui.dialog() as dialog, ui.card().classes('w-96'):
                ui.label('Add New Product').classes('text-xl font-bold mb-4')
                
                name_input = ui.input('Product Name').classes('w-full mb-2')
                description_input = ui.textarea('Description').classes('w-full mb-2')
                price_input = ui.number('Price', min=0, step=0.01).classes('w-full mb-2')
                size_input = ui.input('Size (e.g., 100ml)').classes('w-full mb-2')
                stock_input = ui.number('Stock Quantity', min=0).classes('w-full mb-2')
                
                # Category selection
                category_select = ui.select(options={}, label='Category').classes('w-full mb-4')
                
                # Load categories
                try:
                    with Session(engine) as db:
                        category_service = CategoryService(db)
                        categories = category_service.get_categories()
                        category_options = {str(cat.id): cat.name for cat in categories}
                        category_select.options = category_options
                except Exception:
                    pass
                
                with ui.row().classes('w-full justify-end gap-2'):
                    ui.button('Cancel', on_click=dialog.close)
                    ui.button('Add Product', on_click=lambda: add_product()).classes('luxury-button')
                
                def add_product():
                    """Add new product."""
                    if not all([name_input.value, price_input.value, category_select.value]):
                        ui.notify('Please fill in required fields', type='warning')
                        return
                    
                    try:
                        with Session(engine) as db:
                            product_service = ProductService(db)
                            product_data = {
                                'name': name_input.value,
                                'description': description_input.value,
                                'price': price_input.value,
                                'size': size_input.value,
                                'stock_quantity': int(stock_input.value or 0),
                                'category_id': int(category_select.value)
                            }
                            
                            product_service.create_product(product_data)
                            ui.notify('Product added successfully!', type='positive')
                            dialog.close()
                            load_products()
                    
                    except Exception as e:
                        ui.notify(f'Error adding product: {str(e)}', type='negative')
            
            dialog.open()
        
        # Initial load
        load_products()
    
    def orders_management():
        """Orders management interface."""
        ui.label('Orders Management').classes('text-2xl font-bold mb-6')
        
        orders_container = ui.column().classes('w-full')
        
        def load_orders():
            """Load and display orders."""
            orders_container.clear()
            
            try:
                with Session(engine) as db:
                    order_service = OrderService(db)
                    orders = order_service.get_all_orders()
                    
                    with orders_container:
                        if orders:
                            for order in orders:
                                with ui.card().classes('w-full mb-4'):
                                    with ui.card_section():
                                        with ui.row().classes('justify-between items-center mb-2'):
                                            ui.label(f'Order #{order.order_number}').classes('text-lg font-bold')
                                            
                                            # Status selector
                                            status_select = ui.select(
                                                options={status.value: status.value.title() for status in OrderStatus},
                                                value=order.status.value,
                                                on_change=lambda e, o=order: update_order_status(o.id, e.value)
                                            ).classes('w-32')
                                        
                                        with ui.row().classes('justify-between mb-2'):
                                            ui.label(f'Customer: {order.user.username}')
                                            ui.label(f'Total: ${order.total_amount:.2f}').classes('font-bold text-yellow-600')
                                        
                                        ui.label(f'Date: {order.created_at.strftime("%B %d, %Y %I:%M %p")}').classes('text-sm text-gray-600')
                                        ui.label(f'Items: {len(order.items)}').classes('text-sm text-gray-600')
                        else:
                            ui.label('No orders found').classes('text-gray-500')
            
            except Exception as e:
                with orders_container:
                    ui.label(f'Error loading orders: {str(e)}').classes('text-red-500')
        
        def update_order_status(order_id: int, new_status: str):
            """Update order status."""
            try:
                with Session(engine) as db:
                    order_service = OrderService(db)
                    order_service.update_order_status(order_id, OrderStatus(new_status))
                    ui.notify('Order status updated', type='positive')
            except Exception as e:
                ui.notify(f'Error updating status: {str(e)}', type='negative')
        
        # Initial load
        load_orders()
    
    def users_management():
        """Users management interface."""
        ui.label('Users Management').classes('text-2xl font-bold mb-6')
        
        users_container = ui.column().classes('w-full')
        
        def load_users():
            """Load and display users."""
            users_container.clear()
            
            try:
                with Session(engine) as db:
                    # Simple query to get all users (you might want to add pagination)
                    from sqlalchemy import select
                    from app.models.user import User
                    
                    stmt = select(User).order_by(User.created_at.desc())
                    users = db.execute(stmt).scalars().all()
                    
                    with users_container:
                        if users:
                            with ui.table(columns=[
                                {'name': 'id', 'label': 'ID', 'field': 'id'},
                                {'name': 'username', 'label': 'Username', 'field': 'username'},
                                {'name': 'email', 'label': 'Email', 'field': 'email'},
                                {'name': 'full_name', 'label': 'Full Name', 'field': 'full_name'},
                                {'name': 'status', 'label': 'Status', 'field': 'status'},
                                {'name': 'admin', 'label': 'Admin', 'field': 'admin'},
                                {'name': 'created', 'label': 'Created', 'field': 'created'}
                            ]).classes('w-full') as table:
                                
                                for user in users:
                                    table.add_row({
                                        'id': user.id,
                                        'username': user.username,
                                        'email': user.email,
                                        'full_name': user.full_name or 'N/A',
                                        'status': 'Active' if user.is_active else 'Inactive',
                                        'admin': 'Yes' if user.is_admin else 'No',
                                        'created': user.created_at.strftime('%Y-%m-%d')
                                    })
                        else:
                            ui.label('No users found').classes('text-gray-500')
            
            except Exception as e:
                with users_container:
                    ui.label(f'Error loading users: {str(e)}').classes('text-red-500')
        
        # Initial load
        load_users()
    
    def analytics_dashboard():
        """Analytics dashboard."""
        ui.label('Analytics Dashboard').classes('text-2xl font-bold mb-6')
        
        try:
            with Session(engine) as db:
                # Get basic statistics
                from sqlalchemy import select, func
                from app.models.user import User
                from app.models.product import Product
                from app.models.order import Order
                
                # Count statistics
                total_users = db.execute(select(func.count(User.id))).scalar()
                total_products = db.execute(select(func.count(Product.id))).scalar()
                total_orders = db.execute(select(func.count(Order.id))).scalar()
                total_revenue = db.execute(select(func.sum(Order.total_amount))).scalar() or 0
                
                # Display statistics
                with ui.row().classes('gap-6 mb-8'):
                    with ui.card().classes('p-6 text-center'):
                        ui.label(str(total_users)).classes('text-3xl font-bold text-blue-600')
                        ui.label('Total Users').classes('text-gray-600')
                    
                    with ui.card().classes('p-6 text-center'):
                        ui.label(str(total_products)).classes('text-3xl font-bold text-green-600')
                        ui.label('Total Products').classes('text-gray-600')
                    
                    with ui.card().classes('p-6 text-center'):
                        ui.label(str(total_orders)).classes('text-3xl font-bold text-yellow-600')
                        ui.label('Total Orders').classes('text-gray-600')
                    
                    with ui.card().classes('p-6 text-center'):
                        ui.label(f'${total_revenue:.2f}').classes('text-3xl font-bold text-purple-600')
                        ui.label('Total Revenue').classes('text-gray-600')
                
                ui.label('More detailed analytics coming soon...').classes('text-gray-600 text-center')
        
        except Exception as e:
            ui.label(f'Error loading analytics: {str(e)}').classes('text-red-500')
    
    page_layout(admin_content, "Admin Dashboard - Versace Perfumes")