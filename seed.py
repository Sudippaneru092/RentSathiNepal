"""
RentSathi Nepal — Database Seeder
Run: python seed.py
Seeds: admin, owners, users, amenities, properties, images, reviews, favorites, chats
"""
from app import create_app, db
from app.models import (
    User, OwnerProfile, RoommateProfile, Property, PropertyImage,
    Amenity, PropertyAmenity, Review, Favorite, Chat, AdminLog
)
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

app = create_app()

# ── Nepal cities with real coordinates ──────────────────────────────────────
CITIES = {
    'Kathmandu':  (27.7172, 85.3240),
    'Lalitpur':   (27.6644, 85.3188),
    'Bhaktapur':  (27.6710, 85.4298),
    'Pokhara':    (28.2096, 83.9856),
    'Chitwan':    (27.5291, 84.3542),
    'Butwal':     (27.7006, 83.4532),
    'Dhangadhi':  (28.6940, 80.5993),
    'Biratnagar': (26.4525, 87.2718),
    'Birgunj':    (27.0104, 84.8777),
    'Dharan':     (26.8120, 87.2835),
}

PROVINCES = {
    'Kathmandu': 'Bagmati', 'Lalitpur': 'Bagmati', 'Bhaktapur': 'Bagmati',
    'Pokhara': 'Gandaki', 'Chitwan': 'Bagmati', 'Butwal': 'Lumbini',
    'Dhangadhi': 'Sudurpashchim', 'Biratnagar': 'Koshi',
    'Birgunj': 'Madhesh', 'Dharan': 'Koshi',
}

DISTRICTS = {
    'Kathmandu': 'Kathmandu', 'Lalitpur': 'Lalitpur', 'Bhaktapur': 'Bhaktapur',
    'Pokhara': 'Kaski', 'Chitwan': 'Chitwan', 'Butwal': 'Rupandehi',
    'Dhangadhi': 'Kailali', 'Biratnagar': 'Morang',
    'Birgunj': 'Parsa', 'Dharan': 'Sunsari',
}

AREAS = {
    'Kathmandu': ['Thamel', 'Baneshwor', 'Koteshwor', 'Balaju', 'Lazimpat',
                  'Kirtipur', 'Budhanilkantha', 'Swayambhu', 'Chabahil', 'Bouddha'],
    'Lalitpur':  ['Pulchowk', 'Jwalakhel', 'Imadol', 'Satdobato', 'Harisiddhi'],
    'Bhaktapur': ['Suryabinayak', 'Sallaghari', 'Katunje'],
    'Pokhara':   ['Lakeside', 'Chipledhunga', 'Prithvi Chowk', 'Bagar', 'Rambazar'],
    'Chitwan':   ['Bharatpur-10', 'Bharatpur-11', 'Ratnanagar', 'Khairahani'],
    'Butwal':    ['Traffic Chowk', 'Buspark', 'Milanchowk', 'Kalikanagar'],
    'Dhangadhi': ['Kailali', 'Tikapur', 'Dhangadhi-4'],
    'Biratnagar':['Buddhanagar', 'Ghantaghar', 'Jahada'],
    'Birgunj':   ['Adarshanagar', 'Powerhouse', 'Ghantaghar'],
    'Dharan':    ['B.P. Chowk', 'Vijaypur', 'Bhedetar'],
}

PROPERTY_TEMPLATES = [
    # (title_template, type, price_range, bedrooms, bathrooms, area_sqft, furnished)
    ("Modern {bd}BHK Flat in {area}",     "flat",      (8000,  25000), 2, 1, 650,  True),
    ("Cozy Single Room near {area}",       "room",      (3000,   8000), 1, 1, 150,  False),
    ("Spacious {bd}BHK House in {area}",   "house",     (15000, 50000), 3, 2, 1200, True),
    ("Luxury Apartment in {area}",         "apartment", (20000, 60000), 3, 2, 1500, True),
    ("Budget Room in {area}",              "room",      (2500,   6000), 1, 1, 120,  False),
    ("2BHK Flat near {area}",              "flat",      (9000,  20000), 2, 1, 700,  True),
    ("Student Hostel near {area}",         "hostel",    (4000,   8000), 1, 1, 100,  False),
    ("Commercial Shutter in {area}",       "shutter",   (10000, 35000), 0, 1, 300,  False),
    ("Family House in {area}",             "house",     (18000, 45000), 4, 3, 1800, True),
    ("Semi-Furnished Flat in {area}",      "flat",      (7000,  18000), 2, 1, 600,  False),
    ("New {bd}BHK Apartment in {area}",    "apartment", (12000, 35000), 2, 2, 900,  True),
    ("Affordable Room in {area}",          "room",      (3500,   7000), 1, 1, 130,  False),
    ("4BHK Bungalow in {area}",           "house",     (35000, 80000), 4, 3, 2500, True),
    ("Office Space in {area}",             "shutter",   (15000, 50000), 0, 1, 500,  False),
    ("Furnished Studio in {area}",         "flat",      (6000,  14000), 1, 1, 350,  True),
]

DESCRIPTIONS = [
    "Well-maintained property with excellent ventilation and natural light. Located in a quiet neighborhood with easy access to public transport, markets, and schools. Ideal for families and working professionals.",
    "Recently renovated property featuring modern interiors and quality fittings. The location offers great connectivity to the city center. Water supply and electricity backup available.",
    "Spacious and airy property perfect for a small family or working professionals. Close to hospitals, schools, and shopping centers. 24/7 security with CCTV surveillance.",
    "Beautiful property in a prime location. High-speed internet connectivity available. Proximity to major offices and commercial areas makes this an ideal choice for professionals.",
    "Clean and comfortable property at an affordable price. The neighborhood is safe and friendly. All essential amenities within walking distance.",
    "Premium property with modern amenities including parking, elevator, and generator backup. The property is in excellent condition and ready to move in.",
    "Cozy and well-furnished property perfect for students and young professionals. Nearby restaurants, cafes, and entertainment options. Flexible lease terms available.",
    "Strategically located property with excellent road connectivity. Suitable for both residential and small commercial purposes. Owner is cooperative and responsive.",
]

AMENITY_LIST = [
    'WiFi', 'Water Supply', 'Electricity Backup', 'Generator',
    'Parking', 'Lift/Elevator', 'Security Guard', 'CCTV',
    'Air Conditioning', 'Balcony', 'Garden', 'Gym',
    'Laundry', 'Kitchen', 'Refrigerator', 'Washing Machine',
    'Cable TV', 'Solar Power', 'Water Heater', 'Swimming Pool',
]

REVIEW_TEXTS = [
    "Great place to live! The owner is very cooperative and the neighborhood is peaceful.",
    "Very clean and well-maintained property. Highly recommended for families.",
    "Good location with easy access to public transport. Value for money.",
    "The property is exactly as described. Happy with my decision to rent here.",
    "Decent place but could use some minor repairs. Overall a good experience.",
    "Excellent property with all amenities. The owner responds quickly to any issues.",
    "Perfect for students. Close to campus and all daily needs are nearby.",
    "Nice and quiet neighborhood. The property has great ventilation and natural light.",
    "The kitchen and bathroom are well-maintained. Would definitely recommend.",
    "Good value for the price. The area is safe and the neighbors are friendly.",
]

OWNER_NAMES = [
    ("Ramesh Sharma",    "ramesh@example.com",   "+977-9841234567"),
    ("Sunita Thapa",     "sunita@example.com",   "+977-9842345678"),
    ("Bikash Pradhan",   "bikash@example.com",   "+977-9843456789"),
    ("Sita Gurung",      "sita@example.com",     "+977-9844567890"),
    ("Deepak Karki",     "deepak@example.com",   "+977-9845678901"),
    ("Hari Adhikari",    "hari@example.com",     "+977-9846789012"),
    ("Mina Shrestha",    "mina@example.com",     "+977-9847890123"),
    ("Prakash Tamang",   "prakash@example.com",  "+977-9848901234"),
]

TENANT_NAMES = [
    ("Anita Maharjan",   "anita@example.com",    "+977-9851234567"),
    ("Rajesh Tamang",    "rajesh@example.com",   "+977-9852345678"),
    ("Priya Adhikari",   "priya@example.com",    "+977-9853456789"),
    ("Suresh KC",        "suresh@example.com",   "+977-9854567890"),
    ("Binita Rai",       "binita@example.com",   "+977-9855678901"),
    ("Nabin Limbu",      "nabin@example.com",    "+977-9856789012"),
    ("Kavita Basnet",    "kavita@example.com",   "+977-9857890123"),
    ("Arun Pokharel",    "arun@example.com",     "+977-9858901234"),
    ("Sangita Bista",    "sangita@example.com",  "+977-9859012345"),
    ("Dipesh Magar",     "dipesh@example.com",   "+977-9850123456"),
]

# Unsplash property images (Nepal-appropriate interiors)
PROPERTY_IMAGES = [
    "https://images.unsplash.com/photo-1560185127-6ed189bf02f4?w=600&q=80",
    "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=600&q=80",
    "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=600&q=80",
    "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=600&q=80",
    "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=600&q=80",
    "https://images.unsplash.com/photo-1556020685-ae41abfc9365?w=600&q=80",
    "https://images.unsplash.com/photo-1583608205776-bfd35f0d9f83?w=600&q=80",
    "https://images.unsplash.com/photo-1574362848149-11496d93a7c7?w=600&q=80",
    "https://images.unsplash.com/photo-1599619351208-3e6c839d6828?w=600&q=80",
    "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=600&q=80",
    "https://images.unsplash.com/photo-1565182999561-18d7dc61c393?w=600&q=80",
    "https://images.unsplash.com/photo-1524758631624-e2822e304c36?w=600&q=80",
    "https://images.unsplash.com/photo-1571939228382-b2f2b585ce15?w=600&q=80",
    "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&q=80",
    "https://images.unsplash.com/photo-1536376072261-38c75010e6c9?w=600&q=80",
]


def clear_data():
    print("🗑  Clearing existing data...")
    db.session.execute(db.text("TRUNCATE TABLE admin_logs, chats, reviews, favorites, property_amenities, property_images, property_documents, vacancy_calendar, reports, properties, owner_profiles, roommate_profiles, amenities, users RESTART IDENTITY CASCADE"))
    db.session.commit()
    print("   Done.")


def seed_amenities():
    print("🌱 Seeding amenities...")
    amenities = []
    for name in AMENITY_LIST:
        a = Amenity(amenity_name=name)
        db.session.add(a)
        amenities.append(a)
    db.session.commit()
    print(f"   Created {len(amenities)} amenities.")
    return Amenity.query.all()


def seed_admin():
    print("👤 Seeding admin user...")
    admin = User(
        full_name='Admin RentSathi',
        email='admin@rentsathi.com.np',
        password=generate_password_hash('admin123'),
        role='admin',
        phone='+977-1-4567890',
        city='Kathmandu',
        district='Kathmandu',
        province='Bagmati',
        account_status='active',
    )
    db.session.add(admin)
    db.session.commit()
    print(f"   Admin: admin@rentsathi.com.np / admin123")
    return admin


def seed_owners(amenities):
    print("🏠 Seeding owners and properties...")
    owners = []
    all_properties = []

    for i, (name, email, phone) in enumerate(OWNER_NAMES):
        # Create owner user
        owner = User(
            full_name=name,
            email=email,
            password=generate_password_hash('owner123'),
            role='owner',
            phone=phone,
            gender=random.choice(['Male', 'Female']),
            occupation='Property Owner',
            city=random.choice(list(CITIES.keys())),
            account_status='active',
            created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365)),
        )
        db.session.add(owner)
        db.session.flush()

        # Create owner profile (verified for first 6, pending for last 2)
        status = 'verified' if i < 6 else 'pending'
        profile = OwnerProfile(
            user_id=owner.id,
            citizenship_number=f"040{random.randint(10000, 99999)}",
            owner_type=random.choice(['individual', 'individual', 'agency']),
            verification_status=status,
        )
        db.session.add(profile)
        owners.append(owner)

        # Each owner creates 3-5 properties
        num_props = random.randint(3, 5)
        for j in range(num_props):
            city = random.choice(list(CITIES.keys()))
            lat, lng = CITIES[city]
            # Add small random offset so each property is unique
            lat += random.uniform(-0.02, 0.02)
            lng += random.uniform(-0.02, 0.02)
            area = random.choice(AREAS.get(city, ['City Center']))
            tmpl = random.choice(PROPERTY_TEMPLATES)
            title_t, ptype, price_range, beds, baths, sqft, furnished = tmpl
            price = random.randint(price_range[0], price_range[1])
            # round to nearest 500
            price = round(price / 500) * 500
            title = title_t.format(area=area, bd=beds)

            # Only verified owner properties are 'verified', others pending
            v_status = 'verified' if status == 'verified' else random.choice(['verified', 'pending'])
            prop = Property(
                owner_id=owner.id,
                title=title,
                description=random.choice(DESCRIPTIONS),
                property_type=ptype,
                price=price,
                province=PROVINCES.get(city, 'Bagmati'),
                district=DISTRICTS.get(city, city),
                city=city,
                area=area,
                address=f"{area}, {city}, Nepal",
                latitude=round(lat, 6),
                longitude=round(lng, 6),
                bedrooms=beds,
                bathrooms=baths,
                furnished=furnished,
                parking=random.choice([True, False]),
                availability_status='available',
                verification_status=v_status,
                status='active',
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 180)),
            )
            db.session.add(prop)
            db.session.flush()

            # Property image (use Unsplash URL stored as image_path)
            img = PropertyImage(
                property_id=prop.id,
                image_path=random.choice(PROPERTY_IMAGES),  # external URL
            )
            db.session.add(img)

            # Assign 2-5 random amenities
            chosen = random.sample(amenities, random.randint(2, 5))
            for am in chosen:
                pa = PropertyAmenity(property_id=prop.id, amenity_id=am.id)
                db.session.add(pa)

            all_properties.append(prop)

    db.session.commit()
    print(f"   Created {len(owners)} owners with {len(all_properties)} properties.")
    return owners, all_properties


def seed_tenants(owners, properties, amenities):
    print("👥 Seeding tenant users...")
    tenants = []

    for name, email, phone in TENANT_NAMES:
        city = random.choice(list(CITIES.keys()))
        tenant = User(
            full_name=name,
            email=email,
            password=generate_password_hash('user123'),
            role='user',
            phone=phone,
            gender=random.choice(['Male', 'Female']),
            occupation=random.choice(['Student', 'Engineer', 'Teacher', 'Doctor',
                                      'Nurse', 'Programmer', 'Business Person']),
            city=city,
            district=DISTRICTS.get(city, city),
            province=PROVINCES.get(city, 'Bagmati'),
            account_status='active',
            created_at=datetime.utcnow() - timedelta(days=random.randint(10, 200)),
        )
        db.session.add(tenant)
        db.session.flush()

        # Roommate profile for some tenants
        if random.random() > 0.4:
            rp = RoommateProfile(
                user_id=tenant.id,
                preferred_city=city,
                budget=random.choice([5000, 8000, 10000, 12000, 15000]),
                occupation=tenant.occupation,
                gender_preference=random.choice(['Male', 'Female', 'Any']),
                smoking_preference=random.choice(['No', 'No', 'Yes']),
                drinking_preference=random.choice(['No', 'Occasionally', 'No']),
                lifestyle=random.choice(['Early riser', 'Night owl', 'Flexible']),
                bio=f"Hi, I am {name.split()[0]}, a {tenant.occupation} looking for a comfortable place to stay.",
            )
            db.session.add(rp)

        tenants.append(tenant)

    db.session.flush()

    # Verified properties only for interactions
    verified_props = [p for p in properties if p.verification_status == 'verified']

    print("   Adding reviews, favorites and messages...")
    for tenant in tenants:
        # Favorites: 2-5 random properties
        fav_props = random.sample(verified_props, min(random.randint(2, 5), len(verified_props)))
        for prop in fav_props:
            fav = Favorite(user_id=tenant.id, property_id=prop.id,
                           created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60)))
            db.session.add(fav)

        # Reviews: 1-3 properties
        reviewed = random.sample(verified_props, min(random.randint(1, 3), len(verified_props)))
        for prop in reviewed:
            rev = Review(
                property_id=prop.id,
                user_id=tenant.id,
                rating=random.randint(3, 5),
                review=random.choice(REVIEW_TEXTS),
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 90)),
            )
            db.session.add(rev)

        # Messages to owners: 1-2
        msg_props = random.sample(verified_props, min(2, len(verified_props)))
        for prop in msg_props:
            chat = Chat(
                sender_id=tenant.id,
                receiver_id=prop.owner_id,
                property_id=prop.id,
                message=random.choice([
                    "Hello, I am interested in renting this property. Is it still available?",
                    "Hi, could you please share more details about the monthly rent and advance?",
                    "Good day! I would like to schedule a visit. When are you available?",
                    "Is the price negotiable? I am looking for long-term rent.",
                    "Can you please confirm if utilities like water and electricity are included?",
                ]),
                sent_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            )
            db.session.add(chat)

    db.session.commit()
    print(f"   Created {len(tenants)} tenants with reviews, favorites, and messages.")
    return tenants


def print_summary():
    print("\n" + "="*55)
    print("  ✅  DATABASE SEEDED SUCCESSFULLY")
    print("="*55)
    print(f"  Users:       {User.query.count()}")
    print(f"    - Admin:   {User.query.filter_by(role='admin').count()}")
    print(f"    - Owners:  {User.query.filter_by(role='owner').count()}")
    print(f"    - Tenants: {User.query.filter_by(role='user').count()}")
    print(f"  Properties:  {Property.query.count()}")
    print(f"    - Verified:{Property.query.filter_by(verification_status='verified').count()}")
    print(f"    - Pending: {Property.query.filter_by(verification_status='pending').count()}")
    print(f"  Amenities:   {Amenity.query.count()}")
    print(f"  Reviews:     {Review.query.count()}")
    print(f"  Favorites:   {Favorite.query.count()}")
    print(f"  Messages:    {Chat.query.count()}")
    print("="*55)
    print("\n  LOGIN CREDENTIALS")
    print("  Admin:  admin@rentsathi.com.np  /  admin123")
    print("  Owner:  ramesh@example.com      /  owner123")
    print("  Tenant: anita@example.com       /  user123")
    print("="*55 + "\n")


if __name__ == '__main__':
    with app.app_context():
        clear_data()
        amenities = seed_amenities()
        seed_admin()
        owners, properties = seed_owners(amenities)
        seed_tenants(owners, properties, amenities)
        print_summary()
