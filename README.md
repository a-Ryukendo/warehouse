# Warehouse Inventory Management System

A Django-based warehouse inventory management system for tracking stock movements and maintaining inventory levels in real-time.

## Features

### Core Functionality
- **Product Management**: Add, edit, and view products with unique IDs
- **Stock Transactions**: Record stock in, stock out, and adjustment transactions
- **Real-time Inventory Tracking**: Automatic inventory balance updates
- **Transaction History**: Complete audit trail of all stock movements
- **Inventory Reports**: Current stock levels with status indicators

### Web Interface
- **Dashboard**: Overview with statistics and recent activity
- **Product Management**: CRUD operations for products
- **Transaction Management**: Add and view stock transactions
- **Inventory Reports**: Searchable inventory status report
- **Responsive Design**: Bootstrap-based modern UI

### API Endpoints
- `GET /inventory/api/products/` - List all products
- `GET /inventory/api/products/{product_id}/` - Get product details with current stock
- `GET /inventory/api/inventory/` - Get current inventory levels
- `GET /inventory/api/transactions/` - List all transactions
- `POST /inventory/api/transactions/add/` - Add new transaction

## Database Schema

### Tables
1. **prodmast** (Product) - Product master data
   - `product_id` (Primary Key) - Unique product identifier
   - `name` - Product name
   - `description` - Product description
   - `unit` - Unit of measurement (PCS, KG, etc.)
   - `created_at`, `updated_at` - Timestamps

2. **stckmain** (StockTransaction) - Transaction headers
   - `transaction_id` (Primary Key) - Auto-incrementing ID
   - `transaction_type` - IN, OUT, or ADJUST
   - `reference_no` - External reference number
   - `notes` - Transaction notes
   - `transaction_date` - Transaction timestamp
   - `created_at` - Record creation timestamp

3. **stckdetail** (StockDetail) - Transaction line items
   - `detail_id` (Primary Key) - Auto-incrementing ID
   - `transaction` (Foreign Key) - Links to stckmain
   - `product` (Foreign Key) - Links to prodmast
   - `quantity` - Transaction quantity
   - `unit_price` - Unit price
   - `total_amount` - Auto-calculated total

4. **InventoryBalance** - Current stock levels (helper table)
   - `product` (Primary Key) - Links to prodmast
   - `current_quantity` - Current stock level
   - `last_updated` - Last update timestamp

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd warehouse_inventory
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Web Interface: http://localhost:8000/
   - Admin Panel: http://localhost:8000/admin/

## Usage

### Adding Products
1. Navigate to Products → Add Product
2. Fill in Product ID, Name, Description, and Unit
3. Save the product

### Recording Transactions
1. Navigate to Transactions → Add Transaction
2. Select transaction type (IN/OUT/ADJUST)
3. Add reference number and notes
4. Add product line items with quantities
5. Save the transaction

### Viewing Inventory
1. Navigate to Inventory Report
2. View current stock levels
3. Use search to filter products
4. Check status indicators (In Stock/Low Stock/Out of Stock)

## API Usage

### Get All Products
```bash
curl http://localhost:8000/inventory/api/products/
```

### Get Product Details
```bash
curl http://localhost:8000/inventory/api/products/PROD001/
```

### Get Current Inventory
```bash
curl http://localhost:8000/inventory/api/inventory/
```

### Add Transaction
```bash
curl -X POST http://localhost:8000/inventory/api/transactions/add/ \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_type": "IN",
    "reference_no": "PO-001",
    "notes": "Initial stock",
    "items": [
      {
        "product_id": "PROD001",
        "quantity": 100,
        "unit_price": 10.50
      }
    ]
  }'
```

## Validation Features

### Input Validation
- Product ID: Required, unique, auto-uppercase
- Product Name: Required, trimmed
- Quantity: Must be greater than 0
- Unit Price: Must be non-negative
- Transaction Type: Must be IN, OUT, or ADJUST

### Business Logic Validation
- Duplicate products not allowed in same transaction
- At least one item required per transaction
- Automatic inventory balance updates
- Transaction atomicity (all-or-nothing)

## Deployment

### For Production
1. Set `DEBUG = False` in settings.py
2. Configure proper database (PostgreSQL recommended)
3. Set up static file serving
4. Configure ALLOWED_HOSTS
5. Use environment variables for sensitive data

### Deployment Platforms
- **Render**: Easy deployment with PostgreSQL
- **PythonAnywhere**: Free hosting with SQLite
- **Heroku**: Cloud platform with add-ons
- **AWS**: Scalable cloud infrastructure

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For support or questions, please open an issue in the repository. 