"""Authentication pages (login, register)."""

from nicegui import ui
from app.frontend.components.layout import page_layout
from app.services.user_service import UserService
from app.core.database import Session, engine
from app.core.auth import AuthManager
import re

@ui.page('/login')
def login_page():
    """User login page."""
    
    def login_content():
        with ui.column().classes('items-center justify-center min-h-screen'):
            with ui.card().classes('w-full max-w-md p-8'):
                ui.label('Login to Your Account').classes('text-2xl font-bold text-center mb-6')
                
                email_input = ui.input('Email', placeholder='your@email.com').classes('w-full mb-4')
                password_input = ui.input('Password', password=True).classes('w-full mb-6')
                
                ui.button('Login', on_click=lambda: handle_login()).classes('luxury-button w-full py-3 text-lg mb-4')
                
                with ui.row().classes('justify-center gap-2'):
                    ui.label("Don't have an account?")
                    ui.link('Register here', '/register').classes('text-yellow-600 hover:underline')
        
        def handle_login():
            """Handle user login."""
            if not email_input.value or not password_input.value:
                ui.notify('Please fill in all fields', type='warning')
                return
            
            try:
                with Session(engine) as db:
                    user_service = UserService(db)
                    user = user_service.authenticate_user(email_input.value, password_input.value)
                    
                    if user:
                        AuthManager.login_user(user.id, user.username, user.is_admin)
                        ui.notify(f'Welcome back, {user.username}!', type='positive')
                        ui.navigate.to('/')
                    else:
                        ui.notify('Invalid email or password', type='negative')
            
            except Exception as e:
                ui.notify(f'Login error: {str(e)}', type='negative')
    
    page_layout(login_content, "Login - Versace Perfumes")

@ui.page('/register')
def register_page():
    """User registration page."""
    
    def register_content():
        with ui.column().classes('items-center justify-center min-h-screen'):
            with ui.card().classes('w-full max-w-md p-8'):
                ui.label('Create Your Account').classes('text-2xl font-bold text-center mb-6')
                
                username_input = ui.input('Username').classes('w-full mb-4')
                email_input = ui.input('Email', placeholder='your@email.com').classes('w-full mb-4')
                full_name_input = ui.input('Full Name').classes('w-full mb-4')
                phone_input = ui.input('Phone Number (Optional)').classes('w-full mb-4')
                password_input = ui.input('Password', password=True).classes('w-full mb-4')
                confirm_password_input = ui.input('Confirm Password', password=True).classes('w-full mb-6')
                
                ui.button('Register', on_click=lambda: handle_register()).classes('luxury-button w-full py-3 text-lg mb-4')
                
                with ui.row().classes('justify-center gap-2'):
                    ui.label("Already have an account?")
                    ui.link('Login here', '/login').classes('text-yellow-600 hover:underline')
        
        def handle_register():
            """Handle user registration."""
            # Validation
            if not all([username_input.value, email_input.value, full_name_input.value, 
                       password_input.value, confirm_password_input.value]):
                ui.notify('Please fill in all required fields', type='warning')
                return
            
            if password_input.value != confirm_password_input.value:
                ui.notify('Passwords do not match', type='warning')
                return
            
            if len(password_input.value) < 6:
                ui.notify('Password must be at least 6 characters long', type='warning')
                return
            
            # Email validation
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email_input.value):
                ui.notify('Please enter a valid email address', type='warning')
                return
            
            try:
                with Session(engine) as db:
                    user_service = UserService(db)
                    
                    # Check if user already exists
                    if user_service.get_user_by_email(email_input.value):
                        ui.notify('Email already registered', type='warning')
                        return
                    
                    if user_service.get_user_by_username(username_input.value):
                        ui.notify('Username already taken', type='warning')
                        return
                    
                    # Create user
                    user_data = {
                        'username': username_input.value,
                        'email': email_input.value,
                        'full_name': full_name_input.value,
                        'phone': phone_input.value if phone_input.value else None,
                        'password': password_input.value
                    }
                    
                    user = user_service.create_user(user_data)
                    
                    # Auto-login after registration
                    AuthManager.login_user(user.id, user.username, user.is_admin)
                    ui.notify(f'Welcome to Versace Perfumes, {user.username}!', type='positive')
                    ui.navigate.to('/')
            
            except Exception as e:
                ui.notify(f'Registration error: {str(e)}', type='negative')
    
    page_layout(register_content, "Register - Versace Perfumes")

@ui.page('/logout')
def logout_page():
    """Logout page."""
    AuthManager.logout_user()
    ui.notify('Logged out successfully', type='positive')
    ui.navigate.to('/')