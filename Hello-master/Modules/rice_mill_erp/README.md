# Rice Mill ERP System

A web-based ERP application designed specifically for rice mill operations.

## Features

- **Dashboard**: Overview of key metrics and quick actions
- **Customer Management**: Add and manage customer information
- **Inventory Management**: Track raw materials and finished products
- **Sales Management**: Create and track sales orders
- **Production Management**: Record production batches and yields

## Rice Mill Specific Features

- Paddy to rice conversion tracking
- Yield percentage calculation
- Rice type categorization (White, Brown, Broken, Bran)
- Quantity management in Kg/Quintal/Ton

## Installation

1. Install Python 3.7+
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python app.py
   ```
2. Open browser and go to `http://localhost:5000`

## Data Storage

Currently uses JSON file storage. For production, integrate with:
- PostgreSQL/MySQL for relational data
- MongoDB for document storage

## Future Enhancements

- User authentication and roles
- Financial accounting module
- Purchase management
- Reports and analytics
- Mobile responsive design
- API endpoints for mobile apps