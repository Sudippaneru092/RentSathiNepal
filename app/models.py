from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'user', 'owner', 'admin'
    gender = db.Column(db.String(20), nullable=True)
    occupation = db.Column(db.String(100), nullable=True)
    profile_image = db.Column(db.String(256), nullable=True)
    province = db.Column(db.String(100), nullable=True)
    district = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    account_status = db.Column(db.String(20), nullable=False, default='active')
    profile_complete = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner_profile = db.relationship('OwnerProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    roommate_profile = db.relationship('RoommateProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    properties = db.relationship('Property', backref='owner', lazy='dynamic', foreign_keys='Property.owner_id')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    sent_messages = db.relationship('Chat', backref='sender', lazy='dynamic', foreign_keys='Chat.sender_id')
    received_messages = db.relationship('Chat', backref='receiver', lazy='dynamic', foreign_keys='Chat.receiver_id')
    reviews = db.relationship('Review', backref='reviewer', lazy='dynamic')
    reports = db.relationship('Report', backref='reporter', lazy='dynamic', foreign_keys='Report.reported_by')
    admin_logs = db.relationship('AdminLog', backref='admin', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.email}>'


class OwnerProfile(db.Model):
    __tablename__ = 'owner_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    citizenship_number = db.Column(db.String(50), nullable=True)
    citizenship_front_image = db.Column(db.String(256), nullable=True)
    citizenship_back_image = db.Column(db.String(256), nullable=True)
    owner_type = db.Column(db.String(50), nullable=True)  # 'individual', 'agency'
    verification_status = db.Column(db.String(20), default='pending')  # 'pending', 'verified', 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<OwnerProfile user_id={self.user_id}>'


class RoommateProfile(db.Model):
    __tablename__ = 'roommate_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    preferred_city = db.Column(db.String(100), nullable=True)
    budget = db.Column(db.Numeric(10, 2), nullable=True)
    occupation = db.Column(db.String(100), nullable=True)
    gender_preference = db.Column(db.String(20), nullable=True)
    smoking_preference = db.Column(db.String(20), nullable=True)
    drinking_preference = db.Column(db.String(20), nullable=True)
    lifestyle = db.Column(db.Text, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<RoommateProfile user_id={self.user_id}>'


class Property(db.Model):
    __tablename__ = 'properties'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    property_type = db.Column(db.String(50), nullable=False)  # 'apartment', 'house', 'room', 'office'
    price = db.Column(db.Numeric(10, 2), nullable=False)
    province = db.Column(db.String(100), nullable=True)
    district = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    area = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    bedrooms = db.Column(db.Integer, default=0)
    bathrooms = db.Column(db.Integer, default=0)
    furnished = db.Column(db.Boolean, default=False)
    parking = db.Column(db.Boolean, default=False)
    availability_status = db.Column(db.String(20), default='available')  # 'available', 'occupied'
    verification_status = db.Column(db.String(20), default='pending')  # 'pending', 'verified', 'rejected'
    status = db.Column(db.String(20), default='active')  # 'active', 'inactive'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    images = db.relationship('PropertyImage', backref='property', lazy='dynamic', cascade='all, delete-orphan')
    documents = db.relationship('PropertyDocument', backref='property', lazy='dynamic', cascade='all, delete-orphan')
    amenities = db.relationship('PropertyAmenity', backref='property', lazy='dynamic', cascade='all, delete-orphan')
    vacancy_calendar = db.relationship('VacancyCalendar', backref='property', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='property', lazy='dynamic', cascade='all, delete-orphan')
    chats = db.relationship('Chat', backref='property', lazy='dynamic')
    reviews = db.relationship('Review', backref='property', lazy='dynamic', cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='property', lazy='dynamic')

    def __repr__(self):
        return f'<Property {self.title}>'

    def get_primary_image(self):
        img = self.images.first()
        if not img:
            return None
        # Return full URL if external, otherwise local static path
        if img.image_path.startswith('http'):
            return img.image_path
        return img.image_path

    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return round(sum(r.rating for r in reviews) / len(reviews), 1)


class Amenity(db.Model):
    __tablename__ = 'amenities'

    id = db.Column(db.Integer, primary_key=True)
    amenity_name = db.Column(db.String(100), nullable=False, unique=True)

    property_amenities = db.relationship('PropertyAmenity', backref='amenity', lazy='dynamic')

    def __repr__(self):
        return f'<Amenity {self.amenity_name}>'


class PropertyAmenity(db.Model):
    __tablename__ = 'property_amenities'

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    amenity_id = db.Column(db.Integer, db.ForeignKey('amenities.id'), nullable=False)

    def __repr__(self):
        return f'<PropertyAmenity property={self.property_id} amenity={self.amenity_id}>'


class PropertyImage(db.Model):
    __tablename__ = 'property_images'

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    image_path = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PropertyImage {self.image_path}>'


class PropertyDocument(db.Model):
    __tablename__ = 'property_documents'

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=True)
    document_file = db.Column(db.String(256), nullable=False)
    verification_status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PropertyDocument {self.document_type}>'


class VacancyCalendar(db.Model):
    __tablename__ = 'vacancy_calendar'

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    available_from = db.Column(db.Date, nullable=False)
    available_until = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='available')

    def __repr__(self):
        return f'<VacancyCalendar property={self.property_id}>'


class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'property_id', name='uq_user_property_favorite'),)

    def __repr__(self):
        return f'<Favorite user={self.user_id} property={self.property_id}>'


class Chat(db.Model):
    __tablename__ = 'chats'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=True)
    message = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Chat sender={self.sender_id} receiver={self.receiver_id}>'


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    review = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Review property={self.property_id} rating={self.rating}>'


class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    reported_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'reviewed', 'resolved'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Report property={self.property_id} status={self.status}>'


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    property_id  = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    tenant_id    = db.Column(db.Integer, db.ForeignKey('users.id'),  nullable=False)
    move_in_date = db.Column(db.Date, nullable=False)
    message      = db.Column(db.Text, nullable=True)
    status       = db.Column(db.String(20), default='pending')  # pending, confirmed, rejected, cancelled
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    property = db.relationship('Property', backref=db.backref('bookings', lazy='dynamic'))
    tenant   = db.relationship('User',     backref=db.backref('bookings', lazy='dynamic'), foreign_keys=[tenant_id])

    def __repr__(self):
        return f'<Booking property={self.property_id} tenant={self.tenant_id} status={self.status}>'


class AdminLog(db.Model):
    __tablename__ = 'admin_logs'

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AdminLog admin={self.admin_id} action={self.action}>'
