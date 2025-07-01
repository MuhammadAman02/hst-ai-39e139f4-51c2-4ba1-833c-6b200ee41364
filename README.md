# Versace Perfume E-commerce Store

A luxury e-commerce platform for Versace perfumes built with NiceGUI, featuring elegant UI design, complete shopping functionality, and comprehensive admin management.

## Features

### Customer Features
- **Elegant Product Catalog**: Browse luxury Versace perfumes with high-quality product displays
- **Advanced Filtering**: Filter products by category, search by name, and view detailed product information
- **Shopping Cart**: Add products to cart, modify quantities, and manage cart contents
- **Secure Checkout**: Complete checkout process with shipping information and order confirmation
- **User Accounts**: Register, login, and manage personal information
- **Order History**: View past orders and track order status
- **Responsive Design**: Optimized for desktop and mobile devices

### Admin Features
- **Product Management**: Add, edit, and manage product inventory
- **Order Management**: View all orders and update order status
- **User Management**: Monitor user accounts and activity
- **Analytics Dashboard**: View store statistics and performance metrics

### Technical Features
- **Modern Architecture**: Built with NiceGUI for rich UI components
- **SQLAlchemy V2**: Modern database ORM with proper type hints
- **Pydantic V2**: Data validation and settings management
- **JWT Authentication**: Secure user authentication and session management
- **Luxury Styling**: Custom CSS with gold/black theme for premium feel

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd versace-perfume-store
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. **Run the application**:
   ```bash
   python main.py
   ```

6. **Access the application**:
   - Open your browser to `http://127.0.0.1:8080`
   - The application will automatically create sample data on first run

## Default Admin Account

- **Email**: admin@versace.com
- **Password**: admin123
- **Note**: Change the admin password in production!

## Project Structure

```
versace-perfume-store/
├── app/
│   ├── core/                   # Core application components
│   │   ├── config.py          # Application settings
│   │   ├── database.py        # Database configuration
│   │   ├── auth.py            # Authentication system
│   │   └── logging.py         # Logging configuration
│   ├── models/                 # Database models
│   │   ├── user.py            # User model
│   │   ├── product.py         # Product and category models
│   │   ├── cart.py            # Shopping cart models
│   │   └── order.py           # Order models
│   ├── services/               # Business logic layer
│   │   ├── user_service.py    # User operations
│   │   ├── product_service.py # Product operations
│   │   ├── cart_service.py    # Cart operations
│   │   └── order_service.py   # Order operations
│   ├── frontend/               # UI components and pages
│   │   ├── components/        # Reusable UI components
│   │   └── pages/             # Application pages
│   └── static/                 # Static assets
├── data/                       # Database files
├── logs/                       # Application logs
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Configuration

The application uses environment variables for configuration. Key settings include:

- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT secret key for authentication
- `TAX_RATE`: Tax rate for orders (default: 8%)
- `SHIPPING_COST`: Standard shipping cost
- `FREE_SHIPPING_THRESHOLD`: Minimum order for free shipping

## Database

The application uses SQLite by default for development. The database includes:

- **Users**: Customer accounts and admin users
- **Categories**: Product categories (Men's, Women's, Unisex)
- **Products**: Perfume products with details and inventory
- **Cart**: Shopping cart functionality
- **Orders**: Order management and history

## Sample Data

The application automatically creates sample data including:
- 3 product categories
- 6 sample Versace perfume products
- Default admin account

## Security Features

- **Password Hashing**: Secure password storage using bcrypt
- **JWT Authentication**: Stateless authentication with JSON Web Tokens
- **Input Validation**: Comprehensive input validation using Pydantic
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- **Session Management**: Secure session handling

## Customization

### Adding New Products
1. Login as admin (admin@versace.com / admin123)
2. Navigate to Admin Dashboard
3. Use the Products tab to add new products

### Styling Customization
- Modify CSS in `app/frontend/components/layout.py`
- Update color scheme by changing the luxury theme variables
- Add new UI components in the components directory

### Database Customization
- Modify models in the `app/models/` directory
- Update services in `app/services/` for business logic changes
- Run the application to auto-create new tables

## Production Deployment

For production deployment:

1. **Change default credentials**:
   - Update admin password
   - Generate secure SECRET_KEY

2. **Database**:
   - Switch to PostgreSQL for production
   - Update DATABASE_URL in environment

3. **Security**:
   - Enable HTTPS
   - Set DEBUG=False
   - Configure proper CORS settings

4. **Performance**:
   - Add database indexing
   - Implement caching
   - Use production WSGI server

## API Endpoints

The application includes RESTful API endpoints:

- `GET /api/products` - List products
- `GET /api/products/{id}` - Get product details
- `POST /api/cart/add` - Add to cart
- `GET /api/cart` - Get cart contents
- `POST /api/orders` - Create order
- `GET /api/orders` - Get user orders

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational and demonstration purposes. Versace is a registered trademark of Gianni Versace S.p.A.

## Support

For support and questions:
- Check the logs in the `logs/` directory
- Review the database schema in `app/models/`
- Examine the service layer for business logic

## Version History

- **v1.0.0**: Initial release with complete e-commerce functionality
  - Product catalog and management
  - Shopping cart and checkout
  - User authentication and accounts
  - Admin dashboard
  - Order management system