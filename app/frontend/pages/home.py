"""Home page with featured products and categories."""

from nicegui import ui
from app.frontend.components.layout import page_layout, product_card
from app.services.product_service import ProductService
from app.services.category_service import CategoryService
from app.core.database import Session, engine

@ui.page('/')
def home_page():
    """Home page with hero section and featured products."""
    
    def home_content():
        # Hero section
        with ui.element('div').classes('bg-black text-white py-20 px-8 text-center'):
            ui.label('VERSACE').classes('text-6xl font-bold tracking-widest text-yellow-400')
            ui.label('LUXURY PERFUMES').classes('text-2xl font-light tracking-wider mt-2')
            ui.label('Discover the essence of Italian luxury and sophistication').classes('text-lg mt-4 text-gray-300')
            
            with ui.row().classes('justify-center mt-8 gap-4'):
                ui.button('Shop Now', on_click=lambda: ui.navigate.to('/products')).classes('luxury-button px-8 py-3 text-lg')
                ui.button('View Collections', on_click=lambda: ui.navigate.to('/products')).classes('border border-yellow-400 text-yellow-400 px-8 py-3 text-lg hover:bg-yellow-400 hover:text-black')
        
        # Categories section
        with ui.element('div').classes('py-16 px-8'):
            ui.label('Shop by Category').classes('text-3xl font-bold text-center text-gray-800 mb-12')
            
            with ui.row().classes('justify-center gap-8 flex-wrap'):
                try:
                    with Session(engine) as db:
                        category_service = CategoryService(db)
                        categories = category_service.get_categories()
                        
                        for category in categories:
                            with ui.card().classes('w-80 cursor-pointer hover:shadow-xl transition-all duration-300'):
                                if category.image_url:
                                    ui.image(category.image_url).classes('w-full h-48 object-cover')
                                else:
                                    with ui.element('div').classes('w-full h-48 bg-gradient-to-br from-gray-800 to-black flex items-center justify-center'):
                                        ui.icon('category', size='4rem').classes('text-yellow-400')
                                
                                with ui.card_section():
                                    ui.label(category.name).classes('text-xl font-semibold text-gray-800')
                                    ui.label(category.description or 'Explore our collection').classes('text-gray-600 mt-2')
                                    ui.button('Browse', 
                                             on_click=lambda c=category: ui.navigate.to(f'/products?category={c.id}')).classes('luxury-button mt-4 w-full')
                
                except Exception as e:
                    ui.label(f'Error loading categories: {str(e)}').classes('text-red-500')
        
        # Featured products section
        with ui.element('div').classes('bg-gray-50 py-16 px-8'):
            ui.label('Featured Products').classes('text-3xl font-bold text-center text-gray-800 mb-12')
            
            with ui.row().classes('justify-center gap-8 flex-wrap'):
                try:
                    with Session(engine) as db:
                        product_service = ProductService(db)
                        featured_products = product_service.get_featured_products(6)
                        
                        for product in featured_products:
                            product_card(product)
                
                except Exception as e:
                    ui.label(f'Error loading products: {str(e)}').classes('text-red-500')
        
        # Features section
        with ui.element('div').classes('py-16 px-8 bg-black text-white'):
            ui.label('Why Choose Versace Perfumes?').classes('text-3xl font-bold text-center text-yellow-400 mb-12')
            
            with ui.row().classes('justify-center gap-12 flex-wrap'):
                features = [
                    {'icon': 'local_shipping', 'title': 'Free Shipping', 'desc': 'On orders over $75'},
                    {'icon': 'verified', 'title': 'Authentic Products', 'desc': '100% genuine Versace fragrances'},
                    {'icon': 'support_agent', 'title': '24/7 Support', 'desc': 'Expert customer service'},
                    {'icon': 'autorenew', 'title': 'Easy Returns', 'desc': '30-day return policy'}
                ]
                
                for feature in features:
                    with ui.column().classes('items-center text-center max-w-xs'):
                        ui.icon(feature['icon'], size='3rem').classes('text-yellow-400 mb-4')
                        ui.label(feature['title']).classes('text-xl font-semibold mb-2')
                        ui.label(feature['desc']).classes('text-gray-300')
    
    page_layout(home_content, "Versace Perfumes - Luxury Fragrances")