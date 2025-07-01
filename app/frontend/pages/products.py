"""Products listing and detail pages."""

from nicegui import ui
from app.frontend.components.layout import page_layout, product_card, add_to_cart_action
from app.services.product_service import ProductService
from app.services.category_service import CategoryService
from app.core.database import Session, engine
from app.core.auth import AuthManager

@ui.page('/products')
def products_page():
    """Products listing page with filtering."""
    
    def products_content():
        with ui.row().classes('w-full gap-8 p-8'):
            # Sidebar with filters
            with ui.column().classes('w-64 bg-white p-6 rounded-lg shadow-lg'):
                ui.label('Filters').classes('text-xl font-bold mb-4')
                
                # Category filter
                ui.label('Category').classes('font-semibold mb-2')
                category_select = ui.select(
                    options={},
                    value=None,
                    on_change=lambda e: filter_products()
                ).classes('w-full mb-4')
                
                # Price range (placeholder for future implementation)
                ui.label('Price Range').classes('font-semibold mb-2')
                ui.label('$0 - $200+').classes('text-gray-600 mb-4')
                
                # Search
                ui.label('Search').classes('font-semibold mb-2')
                search_input = ui.input(
                    placeholder='Search products...',
                    on_change=lambda e: filter_products()
                ).classes('w-full')
                
                # Load categories for filter
                try:
                    with Session(engine) as db:
                        category_service = CategoryService(db)
                        categories = category_service.get_categories()
                        category_options = {'all': 'All Categories'}
                        category_options.update({str(cat.id): cat.name for cat in categories})
                        category_select.options = category_options
                        category_select.value = 'all'
                except Exception as e:
                    ui.notify(f'Error loading categories: {str(e)}', type='negative')
            
            # Products grid
            with ui.column().classes('flex-1'):
                ui.label('Our Products').classes('text-3xl font-bold mb-8')
                
                products_container = ui.row().classes('gap-6 flex-wrap')
                
                def filter_products():
                    """Filter and display products."""
                    products_container.clear()
                    
                    try:
                        with Session(engine) as db:
                            product_service = ProductService(db)
                            
                            # Get filter values
                            category_id = None
                            if category_select.value and category_select.value != 'all':
                                category_id = int(category_select.value)
                            
                            search_term = search_input.value if search_input.value else None
                            
                            # Get filtered products
                            products = product_service.get_products(
                                category_id=category_id,
                                search=search_term
                            )
                            
                            with products_container:
                                if products:
                                    for product in products:
                                        product_card(product)
                                else:
                                    ui.label('No products found matching your criteria.').classes('text-gray-500 text-center w-full')
                    
                    except Exception as e:
                        with products_container:
                            ui.label(f'Error loading products: {str(e)}').classes('text-red-500')
                
                # Initial load
                filter_products()
    
    page_layout(products_content, "Products - Versace Perfumes")

@ui.page('/product/{product_id}')
def product_detail_page(product_id: int):
    """Individual product detail page."""
    
    def product_detail_content():
        try:
            with Session(engine) as db:
                product_service = ProductService(db)
                product = product_service.get_product(product_id)
                
                if not product:
                    ui.label('Product not found').classes('text-2xl text-center text-red-500 mt-20')
                    ui.button('Back to Products', on_click=lambda: ui.navigate.to('/products')).classes('mt-4')
                    return
                
                with ui.row().classes('w-full gap-12 p-8'):
                    # Product image
                    with ui.column().classes('w-1/2'):
                        if product.image_url:
                            ui.image(product.image_url).classes('w-full max-w-md rounded-lg shadow-lg')
                        else:
                            with ui.element('div').classes('w-full max-w-md h-96 bg-gray-200 rounded-lg flex items-center justify-center'):
                                ui.icon('fragrance', size='6rem').classes('text-gray-400')
                    
                    # Product details
                    with ui.column().classes('w-1/2 gap-6'):
                        ui.label(product.name).classes('text-4xl font-bold text-gray-800')
                        ui.label(product.category.name).classes('text-lg text-gray-600')
                        
                        ui.label(f'${product.price:.2f}').classes('text-3xl font-bold text-yellow-600 mt-4')
                        
                        if product.size:
                            ui.label(f'Size: {product.size}').classes('text-lg text-gray-700')
                        
                        # Stock status
                        if product.stock_quantity > 0:
                            ui.label(f'{product.stock_quantity} in stock').classes('text-green-600 font-semibold')
                        else:
                            ui.label('Out of stock').classes('text-red-600 font-semibold')
                        
                        # Description
                        if product.description:
                            ui.label('Description').classes('text-xl font-semibold mt-6 mb-2')
                            ui.label(product.description).classes('text-gray-700 leading-relaxed')
                        
                        # Add to cart section
                        if product.stock_quantity > 0:
                            with ui.row().classes('items-center gap-4 mt-8'):
                                quantity_input = ui.number(
                                    label='Quantity',
                                    value=1,
                                    min=1,
                                    max=product.stock_quantity
                                ).classes('w-24')
                                
                                if AuthManager.is_authenticated():
                                    ui.button(
                                        'Add to Cart',
                                        on_click=lambda: add_to_cart_with_quantity(product.id, quantity_input.value)
                                    ).classes('luxury-button px-8 py-3 text-lg')
                                else:
                                    ui.button(
                                        'Login to Purchase',
                                        on_click=lambda: ui.navigate.to('/login')
                                    ).classes('luxury-button px-8 py-3 text-lg')
                        
                        # Additional actions
                        with ui.row().classes('gap-4 mt-6'):
                            ui.button('Back to Products', on_click=lambda: ui.navigate.to('/products')).classes('border border-gray-400 text-gray-700')
                
                # Reviews section (placeholder for future implementation)
                with ui.element('div').classes('w-full mt-16 p-8 bg-gray-50 rounded-lg'):
                    ui.label('Customer Reviews').classes('text-2xl font-bold mb-6')
                    ui.label('Reviews feature coming soon...').classes('text-gray-600')
        
        except Exception as e:
            ui.label(f'Error loading product: {str(e)}').classes('text-red-500 text-center mt-20')
    
    def add_to_cart_with_quantity(product_id: int, quantity: int):
        """Add product to cart with specified quantity."""
        from app.services.cart_service import CartService
        
        try:
            with Session(engine) as db:
                cart_service = CartService(db)
                cart_service.add_to_cart(AuthManager.get_current_user_id(), product_id, int(quantity))
                ui.notify(f'Added {int(quantity)} item(s) to cart!', type='positive')
        except Exception as e:
            ui.notify(f'Error adding to cart: {str(e)}', type='negative')
    
    page_layout(product_detail_content, "Product Details - Versace Perfumes")