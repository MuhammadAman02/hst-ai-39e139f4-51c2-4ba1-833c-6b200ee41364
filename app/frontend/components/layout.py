"""Layout components for the application."""

from nicegui import ui
from app.core.auth import AuthManager
from app.core.config import settings

def create_header():
    """Create the main header with navigation."""
    with ui.header().classes('bg-black text-white shadow-lg'):
        with ui.row().classes('w-full items-center justify-between px-4'):
            # Logo and brand
            with ui.row().classes('items-center gap-4'):
                ui.icon('diamond', size='2rem').classes('text-yellow-400')
                ui.label('VERSACE').classes('text-2xl font-bold tracking-wider')
                ui.label('PERFUMES').classes('text-sm text-yellow-400 font-light')
            
            # Navigation menu
            with ui.row().classes('items-center gap-6'):
                ui.link('Home', '/').classes('text-white hover:text-yellow-400 transition-colors')
                ui.link('Products', '/products').classes('text-white hover:text-yellow-400 transition-colors')
                
                if AuthManager.is_authenticated():
                    ui.link('Cart', '/cart').classes('text-white hover:text-yellow-400 transition-colors')
                    ui.link('Orders', '/orders').classes('text-white hover:text-yellow-400 transition-colors')
                    
                    if AuthManager.is_admin():
                        ui.link('Admin', '/admin').classes('text-white hover:text-yellow-400 transition-colors')
                    
                    with ui.button(icon='account_circle').classes('text-white'):
                        with ui.menu():
                            ui.menu_item(f'Welcome, {AuthManager.get_current_username()}')
                            ui.separator()
                            ui.menu_item('Logout', on_click=lambda: logout_user())
                else:
                    ui.link('Login', '/login').classes('text-white hover:text-yellow-400 transition-colors')
                    ui.link('Register', '/register').classes('text-white hover:text-yellow-400 transition-colors')

def logout_user():
    """Handle user logout."""
    AuthManager.logout_user()
    ui.notify('Logged out successfully', type='positive')
    ui.navigate.to('/')

def create_footer():
    """Create the main footer."""
    with ui.footer().classes('bg-gray-900 text-white p-8'):
        with ui.row().classes('w-full justify-between'):
            with ui.column().classes('gap-2'):
                ui.label('VERSACE PERFUMES').classes('text-xl font-bold text-yellow-400')
                ui.label('Luxury fragrances for the discerning individual').classes('text-gray-300')
                ui.label('© 2025 Versace Perfumes Store. All rights reserved.').classes('text-sm text-gray-400')
            
            with ui.column().classes('gap-2'):
                ui.label('Customer Service').classes('font-semibold text-yellow-400')
                ui.label('Contact Us').classes('text-gray-300 cursor-pointer hover:text-white')
                ui.label('Shipping Info').classes('text-gray-300 cursor-pointer hover:text-white')
                ui.label('Returns').classes('text-gray-300 cursor-pointer hover:text-white')
            
            with ui.column().classes('gap-2'):
                ui.label('Follow Us').classes('font-semibold text-yellow-400')
                with ui.row().classes('gap-2'):
                    ui.icon('facebook').classes('text-2xl text-gray-300 cursor-pointer hover:text-white')
                    ui.icon('instagram').classes('text-2xl text-gray-300 cursor-pointer hover:text-white')
                    ui.icon('twitter').classes('text-2xl text-gray-300 cursor-pointer hover:text-white')

def page_layout(content_func, title: str = "Versace Perfumes"):
    """Standard page layout wrapper."""
    ui.page_title = title
    
    # Add custom CSS for luxury styling
    ui.add_head_html('''
    <style>
        .luxury-card {
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            border: 1px solid #ffd700;
            box-shadow: 0 8px 32px rgba(255, 215, 0, 0.1);
        }
        .luxury-button {
            background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
            color: #000;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .luxury-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(255, 215, 0, 0.3);
        }
        .product-card {
            transition: all 0.3s ease;
            border: 1px solid #333;
        }
        .product-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
            border-color: #ffd700;
        }
        .price-tag {
            color: #ffd700;
            font-weight: bold;
            font-size: 1.2rem;
        }
    </style>
    ''')
    
    create_header()
    
    with ui.column().classes('min-h-screen bg-gray-100'):
        content_func()
    
    create_footer()

def product_card(product, show_add_to_cart=True):
    """Reusable product card component."""
    with ui.card().classes('product-card w-80 bg-white'):
        # Product image
        if product.image_url:
            ui.image(product.image_url).classes('w-full h-48 object-cover')
        else:
            with ui.element('div').classes('w-full h-48 bg-gray-200 flex items-center justify-center'):
                ui.icon('fragrance', size='4rem').classes('text-gray-400')
        
        with ui.card_section():
            # Product name and category
            ui.label(product.name).classes('text-lg font-semibold text-gray-800')
            ui.label(product.category.name).classes('text-sm text-gray-500')
            
            # Price
            ui.label(f'${product.price:.2f}').classes('price-tag mt-2')
            
            # Size if available
            if product.size:
                ui.label(f'Size: {product.size}').classes('text-sm text-gray-600')
            
            # Stock status
            if product.stock_quantity > 0:
                ui.label(f'{product.stock_quantity} in stock').classes('text-sm text-green-600')
            else:
                ui.label('Out of stock').classes('text-sm text-red-600')
            
            # Action buttons
            with ui.row().classes('w-full justify-between mt-4'):
                ui.button('View Details', on_click=lambda p=product: ui.navigate.to(f'/product/{p.id}')).classes('flex-1')
                
                if show_add_to_cart and product.stock_quantity > 0 and AuthManager.is_authenticated():
                    ui.button('Add to Cart', 
                             on_click=lambda p=product: add_to_cart_action(p.id)).classes('luxury-button flex-1 ml-2')

def add_to_cart_action(product_id: int):
    """Add product to cart action."""
    from app.services.cart_service import CartService
    from app.core.database import Session, engine
    
    if not AuthManager.is_authenticated():
        ui.notify('Please login to add items to cart', type='warning')
        ui.navigate.to('/login')
        return
    
    try:
        with Session(engine) as db:
            cart_service = CartService(db)
            cart_service.add_to_cart(AuthManager.get_current_user_id(), product_id, 1)
            ui.notify('Product added to cart!', type='positive')
    except Exception as e:
        ui.notify(f'Error adding to cart: {str(e)}', type='negative')