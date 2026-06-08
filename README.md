# RentSathi Nepal — Flask Rental Website

A full-featured rental property listing platform for Nepal, built with Flask, PostgreSQL, Bootstrap 5.

## Features

- **Two roles**: Tenant/Roommate Seeker and Property Owner
- **Authentication**: Register, Login, Logout with role-based access
- **Property listings**: Search by city, type, price range, furnishing
- **Owner dashboard**: Add, edit, delete properties with image uploads
- **User dashboard**: Save favorites, roommate profile, messages
- **Admin panel**: Verify properties & owners, manage users, handle reports
- **Reviews & Ratings**: Users can review properties
- **Messaging**: Tenants can contact property owners directly
- **Report system**: Report suspicious listings

## Project Structure

```
rental_website/
├── app/
│   ├── __init__.py          # App factory
│   ├── models.py            # SQLAlchemy models
│   ├── auth/                # Auth blueprint (login/register/logout)
│   ├── main/                # Public routes (index, property detail)
│   ├── owner/               # Owner routes (dashboard, add/edit/delete property)
│   ├── user/                # User routes (dashboard, profile, favorites, messages)
│   ├── admin/               # Admin routes (verifications, reports, logs)
│   ├── static/
│   │   ├── css/style.css    # Custom styles
│   │   └── uploads/         # Uploaded files
│   └── templates/           # Jinja2 templates
├── config.py
├── requirements.txt
├── run.py
└── .env.example
```

## Setup

### 1. Create virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
Copy `.env.example` to `.env` and update values:
```bash
cp .env.example .env
```
Edit `.env`:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://postgres:yourpassword@localhost/rental_db
```

### 4. Create the PostgreSQL database
```sql
CREATE DATABASE rental_db;
```

### 5. Run the application
```bash
python run.py
```

Visit `http://localhost:5000`

## Creating an Admin User

After the DB tables are created, run this in a Python shell:
```python
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    admin = User(
        full_name='Admin User',
        email='admin@rentsathi.com',
        password=generate_password_hash('admin123'),
        role='admin',
        account_status='active'
    )
    db.session.add(admin)
    db.session.commit()
    print('Admin created!')
```

## Seeding Amenities (optional)

```python
from app import create_app, db
from app.models import Amenity

app = create_app()
amenities = [
    'WiFi', 'Water Supply', 'Electricity Backup', 'Generator',
    'Parking', 'Lift/Elevator', 'Security Guard', 'CCTV',
    'Air Conditioning', 'Balcony', 'Garden', 'Gym',
    'Laundry', 'Kitchen', 'Refrigerator', 'Washing Machine',
    'Cable TV', 'Solar Power', 'Water Heater', 'Swimming Pool'
]
with app.app_context():
    for name in amenities:
        if not Amenity.query.filter_by(amenity_name=name).first():
            db.session.add(Amenity(amenity_name=name))
    db.session.commit()
    print('Amenities seeded!')
```
