"""Shopping cart page."""

from nicegui import ui
from app.frontend.components.layout import page_layout
from app.services.cart_service import CartService
from app.core.database import Session, engine
from app.core.auth import AuthManager, require_auth
from app.core.config import settings

@ui.page('/cart')
@require_auth
def cart_page():
    """Shopping cart page."""
    
    def cart_content():
        ui.label('Shopping Cart').classes('text-3xl font-bold mb-8 text-center')
        
        cart_container = ui.column().classes('w-full max-w-4xl mx-auto')
        
        def load_cart():
            """Load and display cart contents."""
            cart_container.clear()
            
            try:
                with Session(engine) as db:
                    cart_service = CartService(db)
                    cart_items = cart_service.get_cart_items(AuthManager.get_current_user_id())
                    
                    if not cart_items:
                        with cart_container:
                            with ui.column().classes('items-center text-center py-20'):
                                ui.icon('shopping_cart', size='4rem').classes('text-gray-400 mb-4')
                                ui.label('Your cart is empty').classes('text-xl text-gray-600 mb-4')
                                ui.button('Continue Shopping', 
                                         on_click=lambda: ui.navigate.to('/products')).classes('luxury-button px-8 py-3')
                        return
                    
                    with cart_container:
                        # Cart items
                        for item in cart_items:
                            with ui.card().classes('w-full mb-4'):
                                with ui.row().classes('items-center gap-6 p-4'):
                                    # Product image
                                    if item.product.image_url:
                                        ui.image(item.product.image_url).classes('w-20 h-20 object-cover rounded')
                                    else:
                                        with ui.element('div').classes('w-20 h-20 bg-gray-200 rounded flex items-center justify-center'):
                                            ui.icon('fragrance', size='2rem').classes('text-gray-400')
                                    
                                    # Product details
                                    with ui.column().classes('flex-1'):
                                        ui.label(item.product.name).classes('text-lg font-semibold')
                                        ui.label(item.product.category.name).classes('text-gray-600')
                                        if item.product.size:
                                            ui.label(f'Size: {item.product.size}').classes('text-sm text-gray-500')
                                    
                                    # Quantity controls
                                    with ui.row().classes('items-center gap-2'):
                                        ui.button('-', 
                                                 on_click=lambda i=item: update_quantity(i.product_id, i.quantity - 1)).classes('w-8 h-8')
                                        ui.label(str(item.quantity)).classes('w-8 text-center font-semibold')
                                        ui.button('+', 
                                                 on_click=lambda i=item: update_quantity(i.product_id, i.quantity + 1)).classes('w-8 h-8')
                                    
                                    # Price
                                    ui.label(f'${item.product.price:.2f}').classes('text-lg font-semibold w-20 text-right')
                                    ui.label(f'${item.product.price * item.quantity:.2f}').classes('text-lg font-bold text-yellow-600 w-24 text-right')
                                    
                                    # Remove button
                                    ui.button(icon='delete', 
                                             on_click=lambda i=item: remove_item(i.product_id)).classes('text-red-500')
                        
                        # Cart summary
                        with ui.card().classes('w-full mt-8 bg-gray-50'):
                            with ui.card_section():
                                ui.label('Order Summary').classes('text-xl font-bold mb-4')
                                
                                subtotal = sum(item.product.price * item.quantity for item in cart_items)
                                tax_amount = subtotal * settings.tax_rate
                                shipping_cost = 0.0 if subtotal >= settings.free_shipping_threshold else settings.shipping_cost
                                total = subtotal + tax_amount + shipping_cost
                                
                                with ui.row().classes('justify-between mb-2'):
                                    ui.label('Subtotal:')
                                    ui.label(f'${subtotal:.2f}')
                                
                                with ui.row().classes('justify-between mb-2'):
                                    ui.label(f'Tax ({settings.tax_rate*100:.0f}%):')
                                    ui.label(f'${tax_amount:.2f}')
                                
                                with ui.row().classes('justify-between mb-2'):
                                    ui.label('Shipping:')
                                    if shipping_cost == 0:
                                        ui.label('FREE').classes('text-green-600 font-semibold')
                                    else:
                                        ui.label(f'${shipping_cost:.2f}')
                                
                                if subtotal < settings.free_shipping_threshold:
                                    remaining = settings.free_shipping_threshold - subtotal
                                    ui.label(f'Add ${remaining:.2f} more for free shipping!').classes('text-sm text-blue-600 mb-2')
                                
                                ui.separator()
                                
                                with ui.row().classes('justify-between mb-4'):
                                    ui.label('Total:').classes('text-xl font-bold')
                                    ui.label(f'${total:.2f}').classes('text-xl font-bold text-yellow-600')
                                
                                with ui.row().classes('gap-4'):
                                    ui.button('Continue Shopping', 
                                             on_click=lambda: ui.navigate.to('/products')).classes('flex-1')
                                    ui.button('Proceed to Checkout', 
                                             on_click=lambda: ui.navigate.to('/checkout')).classes('luxury-button flex-1')
            
            except Exception as e:
                with cart_container:
                    ui.label(f'Error loading cart: {str(e)}').classes('text-red-500')
        
        def update_quantity(product_id: int, new_quantity: int):
            """Update item quantity in cart."""
            try:
                with Session(engine) as db:
                    cart_service = CartService(db)
                    if new_quantity <= 0:
                        cart_service.remove_from_cart(AuthManager.get_current_user_id(), product_id)
                        ui.notify('Item removed from cart', type='info')
                    else:
                        cart_service.update_cart_item(AuthManager.get_current_user_id(), product_id, new_quantity)
                        ui.notify('Cart updated', type='positive')
                    load_cart()
            except Exception as e:
                ui.notify(f'Error updating cart: {str(e)}', type='negative')
        
        def remove_item(product_id: int):
            """Remove item from cart."""
            try:
                with Session(engine) as db:
                    cart_service = CartService(db)
                    cart_service.remove_from_cart(AuthManager.get_current_user_id(), product_id)
                    ui.notify('Item removed from cart', type='info')
                    load_cart()
            except Exception as e:
                ui.notify(f'Error removing item: {str(e)}', type='negative')
        
        # Initial load
        load_cart()
    
    page_layout(cart_content, "Shopping Cart - Versace Perfumes")