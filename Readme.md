# E-commerce Admin API

A back-end API that powers a web admin dashboard for e-commerce managers, providing detailed insights into sales, revenue, and inventory status, as well as allowing new product registration. The framework used for this is FastAPI(Python) and APIs are RESTful. The DB is Postgres.

## Features

### Sales Status
- Retrieve, filter, and analyze sales data
- Analyze revenue on a daily, weekly, monthly, and annual basis
- Compare revenue across different periods and categories
- Provide sales data by date range, product, and category

### Inventory Management
- View current inventory status, including low stock alerts
- Update inventory levels and track changes over time
- View inventory history

## Technologies Used

- Python 3.9
- FastAPI
- SQLAlchemy
- PostgreSQL
- Docker & Docker Compose

## Database Schema

The database includes the following tables:
- `categories`: Product categories
- `products`: Product information
- `inventory`: Current inventory levels
- `inventory_logs`: History of inventory changes
- `sales`: Sales transaction data
- `sale_items`: Individual items sold in each transaction

## Getting Started

### Prerequisites

- Docker and Docker Compose

### Running the Application

1. Clone the repository
2. Start the application using Docker Compose:
```
docker-compose up
```
3. The API will be available at http://localhost:6061
4. Access the API documentation at http://localhost:6061/docs

## API Endpoints

### Categories
- `GET /api/v1/categories/`: Get all categories
- `GET /api/v1/categories/{category_id}`: Get a specific category
- `POST /api/v1/categories/`: Create a new category

### Products
- `GET /api/v1/products/`: Get all products
- `GET /api/v1/products/{product_id}`: Get a specific product
- `POST /api/v1/products/`: Create a new product

### Inventory
- `GET /api/v1/inventory/`: Get all inventory
- `GET /api/v1/inventory/{product_id}`: Get inventory for a specific product
- `PUT /api/v1/inventory/{product_id}`: Update inventory for a product
- `GET /api/v1/inventory/low-stock/`: Get products with low stock
- `GET /api/v1/inventory/history/{product_id}`: Get inventory history for a product

### Sales
- `GET /api/v1/sales/`: Get all sales
- `GET /api/v1/sales/{sale_id}`: Get a specific sale
- `POST /api/v1/sales/`: Create a new sale

### Analytics
- `GET /api/v1/analytics/sales/`: Get sales summary for a date range
- `GET /api/v1/analytics/revenue/{period}`: Get revenue comparison for a period
- `POST /api/v1/analytics/product-sales/`: Get product sales by date range

## Demo Data

The application is seeded with demo data including:
- 5 product categories
- 25 products (5 in each category)
- Initial inventory for all products
- 500 random sales transactions over the past year

## Testing

The application includes comprehensive test suites to ensure all functionality works correctly:

### Running Tests

To run the complete test suite:

```bash
# From the services/dashboard directory
./run_tests.sh
```

### Test Categories

1. **Unit/Integration Tests**: Tests all API endpoints and functionality
   - Located in `services/dashboard/tests/test_api.py`

2. **Data Seeding Tests**: Tests the demo data generation script
   - Located in `services/dashboard/tests/test_seed_data.py`

3. **Load Tests**: Performance testing with Locust
   - Located in `services/dashboard/tests/locustfile.py`
   - Run with: `locust -f tests/locustfile.py`
   - Open http://localhost:8089 in your browser to control the load test

For more details about the test suite, see `services/dashboard/tests/README.md`.

## License

This project is licensed under the MIT License.
