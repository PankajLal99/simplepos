# Simple POS - Keyboard-Navigable Point of Sale System

A modern, keyboard-friendly Point of Sale (POS) system built with Django 5.0.2 and Bootstrap 5.3. Designed for efficiency and ease of use, this system allows quick product search, invoice creation, and printing through keyboard shortcuts and a clean interface.

## Features

### 🎯 Core Features
- Real-time product search with keyboard navigation
- Dynamic invoice creation and management
- Print-ready invoice generation
- Mobile, tablet, and desktop responsive design
- Admin interface for product management

### ⌨️ Keyboard Shortcuts
- `/` - Focus on product search
- `Escape` - Clear search input
- `Arrow Up/Down` - Navigate search results
- `Enter` - Select highlighted product
- `Ctrl + P` - Print current invoice
- `Ctrl + N` - Start new invoice

### 📱 Responsive Design
- Mobile-first approach
- Adaptive grid system
- Touch-friendly controls
- Print-optimized invoice layout

## Tech Stack

- **Backend**: Django 5.0.2
- **Frontend**: Bootstrap 5.3
- **Database**: SQLite (default)
- **JavaScript**: jQuery 3.6.0
- **Icons**: Bootstrap Icons 1.11.0

## Prerequisites

- Python 3.11
- Conda (recommended for environment management)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd simplepos
```

2. Create and activate Conda environment:
```bash
conda create -n ITSpos python=3.11
conda activate ITSpos
```

3. Install dependencies:
```bash
pip install django==5.0.2
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Usage Guide

### Admin Interface
1. Access the admin panel at `http://localhost:8000/admin`
2. Log in with your superuser credentials
3. Add products with:
   - Name
   - SKU (unique identifier)
   - Price
   - Stock quantity

### POS Interface
1. Access the main POS interface at `http://localhost:8000`
2. Search for products:
   - Type product name in the search box
   - Use arrow keys to navigate results
   - Press Enter to select
3. Manage invoice:
   - Products are automatically added to the current invoice
   - Adjust quantities using +/- buttons or direct input
   - Remove items using the trash icon
4. Print invoice:
   - Click "Print Invoice" or press Ctrl+P
   - Invoice opens in a new tab
   - Use browser's print function or the print button

## Project Structure

```
simplepos/                      # Root project directory
├── pos/                        # Main application
│   ├── migrations/            # Database migrations
│   │   └── __init__.py
│   ├── templates/            # HTML templates
│   │   └── pos/
│   │       ├── base.html     # Base template with common elements
│   │       ├── home.html     # Main POS interface
│   │       └── print.html    # Invoice print template
│   ├── __init__.py
│   ├── admin.py              # Admin interface configuration
│   ├── apps.py              # App configuration
│   ├── models.py            # Database models
│   ├── tests.py             # Test cases
│   ├── urls.py              # URL routing
│   └── views.py             # View functions
├── simplepos/                # Project settings
│   ├── __init__.py
│   ├── asgi.py             # ASGI configuration
│   ├── settings.py         # Project settings
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py             # WSGI configuration
├── static/                  # Static files
│   ├── css/                # CSS files
│   ├── js/                 # JavaScript files
│   └── img/                # Image files
├── media/                  # User-uploaded files
├── templates/              # Project-level templates
├── .gitignore             # Git ignore rules
├── manage.py              # Django management script
├── README.md              # Project documentation
└── requirements.txt        # Project dependencies
```

### Key Files and Their Purposes

#### Application Files (`pos/`)
- `models.py`: Defines database models (Product, Invoice, InvoiceItem)
- `views.py`: Contains view functions for handling requests
- `urls.py`: Defines URL patterns for the application
- `admin.py`: Configures the admin interface
- `templates/`: Contains HTML templates for the application

#### Project Files (`simplepos/`)
- `settings.py`: Project settings and configuration
- `urls.py`: Main URL configuration
- `wsgi.py`: WSGI application entry point
- `asgi.py`: ASGI application entry point

#### Template Files
- `base.html`: Base template with common elements
- `home.html`: Main POS interface with search and invoice management
- `print.html`: Invoice print template

#### Static Files
- CSS, JavaScript, and image files
- Bootstrap and jQuery libraries
- Custom styles and scripts

#### Configuration Files
- `requirements.txt`: Project dependencies
- `.gitignore`: Git ignore rules
- `manage.py`: Django management script

## Dependencies

The project requires the following Python packages (specified in `requirements.txt`):

```
Django==5.0.2
python-dotenv
Pillow
django-crispy-forms
crispy-bootstrap5
```

Install dependencies using:
```bash
pip install -r requirements.txt
```

## Models

### Product
- `name`: Product name
- `sku`: Unique stock keeping unit
- `price`: Decimal price
- `stock`: Available quantity
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Invoice
- `invoice_number`: Unique invoice identifier
- `date`: Invoice date and time
- `total_amount`: Total invoice amount
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### InvoiceItem
- `invoice`: Foreign key to Invoice
- `product`: Foreign key to Product
- `quantity`: Item quantity
- `price`: Item price at time of sale
- `subtotal`: Quantity × Price

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Django Documentation
- Bootstrap Documentation
- Design principles from designprinciples.txt 