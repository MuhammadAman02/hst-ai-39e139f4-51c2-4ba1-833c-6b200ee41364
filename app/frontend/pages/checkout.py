"""Checkout and order pages."""

from nicegui import ui
from app.frontend.components.layout import page_layout
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.services.user_service import UserService
from app.core.database import Session, engine
from app.core.auth import AuthManager, require_auth
from app.core.config import settings

@ui.page('/checkout')
@require_auth
def checkout_page():
    """Checkout page for order completion."""
    
    def checkout_content():
        ui.label('Checkout').classes('text-3xl font-bold mb-8 text-center')
        
        # Check if cart has items
        try:
            with Session(engine) as db:
                cart_service = CartService(db)
                cart_items = cart_service.get_cart_items(AuthManager.get_current_user_id())
                
                if not cart_items:
                    with ui.column().classes('items-center text-center py-20'):
                        ui.label('Your cart is empty').classes('text-xl text-gray-600 mb-4')
                        ui.button('Continue Shopping', 
                                 on_click=lambda: ui.navigate.to('/products')).classes('luxury-button px-8 py-3')
                    return
        except Exception as e:
            ui.label(f'Error loading cart: {str(e)}').classes('text-red-500')
            return
        
        with ui.row().classes('w-full max-w-6xl mx-auto gap-8'):
            # Shipping form
            with ui.column().classes('flex-1'):
                with ui.card().classes('w-full'):
                    with ui.card_section():
                        ui.label('Shipping Information').classes('text-xl font-bold mb-4')
                        
                        # Pre-fill with user data if available
                        user_data = {}
                        try:
                            with Session(engine) as db:
                                user_service = UserService(db)
                                user = user_service.get_user(AuthManager.get_current_user_id())
                                if user:
                                    user_data = {
                                        'full_name': user.full_name or '',
                                        'phone': user.phone or '',
                                        'address': user.address or ''
                                    }
                        except Exception:
                            pass
                        
                        name_input = ui.input('Full Name', value=user_data.get('full_name', '')).classes('w-full mb-4')
                        phone_input = ui.input('Phone Number', value=user_data.get('phone', '')).classes('w-full mb-4')
                        address_input = ui.textarea('Shipping Address', value=user_data.get('address', '')).classes('w-full mb-4')
                        
                        ui.label('Payment Method').classes('font-semibold mb-2')
                        payment_method = ui.select(
                            options=['Credit Card', 'Debit Card', 'PayPal'],
                            value='Credit Card'
                        ).classes('w-full mb-4')
                        
                        # Payment form (simplified for demo)
                        with ui.expansion('Payment Details', icon='payment').classes('w-full mb-4'):
                            ui.input('Card Number', placeholder='1234 5678 9012 3456').classes('w-full mb-2')
                            with ui.row().classes('gap-4'):
                                ui.input('MM/YY', placeholder='12/25').classes('flex-1')
                                ui.input('CVV', placeholder='123').classes('flex-1')
                            ui.input('Cardholder Name').classes('w-full mt-2')
            
            # Order summary
            with ui.column().classes('w-96'):
                with ui.card().classes('w-full'):
                    with ui.card_section():
                        ui.label('Order Summary').classes('text-xl font-bold mb-4')
                        
                        # Cart items summary
                        try:
                            subtotal = sum(item.product.price * item.quantity for item in cart_items)
                            tax_amount = subtotal * settings.tax_rate
                            shipping_cost = 0.0 if subtotal >= settings.free_shipping_threshold else settings.shipping_cost
                            total = subtotal + tax_amount + shipping_cost
                            
                            for item in cart_items:
                                with ui.row().classes('justify-between mb-2'):
                                    ui.label(f'{item.product.name} x{item.quantity}').classes('text-sm')
                                    ui.label(f'${item.product.price * item.quantity:.2f}').classes('text-sm')
                            
                            ui.separator()
                            
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
                            
                            ui.separator()
                            
                            with ui.row().classes('justify-between mb-4'):
                                ui.label('Total:').classes('text-lg font-bold')
                                ui.label(f'${total:.2f}').classes('text-lg font-bold text-yellow-600')
                            
                            ui.button('Place Order', 
                                     on_click=lambda: place_order()).classes('luxury-button w-full py-3 text-lg')
                        
                        except Exception as e:
                            ui.label(f'Error calculating total: {str(e)}').classes('text-red-500')
        
        def place_order():
            """Process the order."""
            # Validate form
            if not name_input.value or not address_input.value:
                ui.notify('Please fill in all required fields', type='warning')
                return
            
            try:
                with Session(engine) as db:
                    cart_service = CartService(db)
                    order_service = OrderService(db)
                    
                    # Get current cart items
                    cart_items = cart_service.get_cart_items(AuthManager.get_current_user_id())
                    
                    if not cart_items:
                        ui.notify('Cart is empty', type='warning')
                        return
                    
                    # Create shipping info
                    shipping_info = {
                        'name': name_input.value,
                        'address': address_input.value,
                        'phone': phone_input.value,
                        'payment_method': payment_method.value
                    }
                    
                    # Create order
                    order = order_service.create_order_from_cart(
                        AuthManager.get_current_user_id(),
                        cart_items,
                        shipping_info
                    )
                    
                    # Clear cart
                    cart_service.clear_cart(AuthManager.get_current_user_id())
                    
                    ui.notify('Order placed successfully!', type='positive')
                    ui.navigate.to(f'/order-confirmation/{order.id}')
            
            except Exception as e:
                ui.notify(f'Error placing order: {str(e)}', type='negative')
    
    page_layout(checkout_content, "Checkout - Versace Perfumes")

@ui.page('/order-confirmation/{order_id}')
@require_auth
def order_confirmation_page(order_id: int):
    """Order confirmation page."""
    
    def confirmation_content():
        try:
            with Session(engine) as db:
                order_service = OrderService(db)
                order = order_service.get_order(order_id)
                
                if not order or order.user_id != AuthManager.get_current_user_id():
                    ui.label('Order not found').classes('text-2xl text-center text-red-500 mt-20')
                    return
                
                with ui.column().classes('items-center text-center max-w-2xl mx-auto'):
                    ui.icon('check_circle', size='4rem').classes('text-green-500 mb-4')
                    ui.label('Order Confirmed!').classes('text-3xl font-bold text-green-600 mb-2')
                    ui.label(f'Order #{order.order_number}').classes('text-xl text-gray-600 mb-8')
                    
                    with ui.card().classes('w-full text-left'):
                        with ui.card_section():
                            ui.label('Order Details').classes('text-xl font-bold mb-4')
                            
                            with ui.row().classes('justify-between mb-2'):
                                ui.label('Order Date:')
                                ui.label(order.created_at.strftime('%B %d, %Y'))
                            
                            with ui.row().classes('justify-between mb-2'):
                                ui.label('Status:')
                                ui.label(order.status.value.title()).classes('text-blue-600 font-semibold')
                            
                            with ui.row().classes('justify-between mb-4'):
                                ui.label('Total:')
                                ui.label(f'${order.total_amount:.2f}').classes('text-lg font-bold text-yellow-600')
                            
                            ui.separator()
                            
                            ui.label('Items Ordered:').classes('font-semibold mt-4 mb-2')
                            for item in order.items:
                                with ui.row().classes('justify-between mb-1'):
                                    ui.label(f'{item.product.name} x{item.quantity}')
                                    ui.label(f'${item.price * item.quantity:.2f}')
                            
                            ui.separator()
                            
                            ui.label('Shipping Address:').classes('font-semibold mt-4 mb-2')
                            ui.label(order.shipping_name)
                            ui.label(order.shipping_address).classes('whitespace-pre-line')
                    
                    with ui.row().classes('gap-4 mt-8'):
                        ui.button('Continue Shopping', 
                                 on_click=lambda: ui.navigate.to('/products')).classes('px-8 py-3')
                        ui.button('View Orders', 
                                 on_click=lambda: ui.navigate.to('/orders')).classes('luxury-button px-8 py-3')
        
        except Exception as e:
            ui.label(f'Error loading order: {str(e)}').classes('text-red-500 text-center mt-20')
    
    page_layout(confirmation_content, "Order Confirmation - Versace Perfumes")

@ui.page('/orders')
@require_auth
def orders_page():
    """User orders history page."""
    
    def orders_content():
        ui.label('My Orders').classes('text-3xl font-bold mb-8 text-center')
        
        try:
            with Session(engine) as db:
                order_service = OrderService(db)
                orders = order_service.get_user_orders(AuthManager.get_current_user_id())
                
                if not orders:
                    with ui.column().classes('items-center text-center py-20'):
                        ui.icon('receipt_long', size='4rem').classes('text-gray-400 mb-4')
                        ui.label('No orders found').classes('text-xl text-gray-600 mb-4')
                        ui.button('Start Shopping', 
                                 on_click=lambda: ui.navigate.to('/products')).classes('luxury-button px-8 py-3')
                    return
                
                for order in orders:
                    with ui.card().classes('w-full max-w-4xl mx-auto mb-6'):
                        with ui.card_section():
                            with ui.row().classes('justify-between items-center mb-4'):
                                ui.label(f'Order #{order.order_number}').classes('text-lg font-bold')
                                ui.label(order.status.value.title()).classes('px-3 py-1 rounded-full bg-blue-100 text-blue-800 text-sm font-semibold')
                            
                            with ui.row().classes('justify-between mb-4'):
                                ui.label(f'Date: {order.created_at.strftime("%B %d, %Y")}')
                                ui.label(f'Total: ${order.total_amount:.2f}').classes('text-lg font-bold text-yellow-600')
                            
                            # Order items
                            ui.label('Items:').classes('font-semibold mb-2')
                            for item in order.items:
                                with ui.row().classes('justify-between mb-1'):
                                    ui.label(f'{item.product.name} x{item.quantity}')
                                    ui.label(f'${item.price * item.quantity:.2f}')
                            
                            with ui.row().classes('gap-4 mt-4'):
                                ui.button('View Details', 
                                         on_click=lambda o=order: ui.navigate.to(f'/order-confirmation/{o.id}'))
                                if order.status.value in ['pending', 'confirmed']:
                                    ui.button('Cancel Order', 
                                             on_click=lambda o=order: cancel_order(o.id)).classes('text-red-600')
        
        except Exception as e:
            ui.label(f'Error loading orders: {str(e)}').classes('text-red-500 text-center')
        
        def cancel_order(order_id: int):
            """Cancel an order."""
            try:
                with Session(engine) as db:
                    order_service = OrderService(db)
                    order_service.cancel_order(order_id)
                    ui.notify('Order cancelled successfully', type='info')
                    ui.navigate.reload()
            except Exception as e:
                ui.notify(f'Error cancelling order: {str(e)}', type='negative')
    
    page_layout(orders_content, "My Orders - Versace Perfumes")