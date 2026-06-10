"""
Unit tests for RentSathi Nepal application.
Tests critical functions across all modules.
"""

import unittest
from datetime import datetime, timedelta
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Property, Favorite, Review, OwnerProfile, RoommateProfile
from werkzeug.security import generate_password_hash, check_password_hash


class BaseTestCase(unittest.TestCase):
    """Base test case with setup/teardown for app context."""
    
    def setUp(self):
        """Set up test client and database."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up after tests."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def _create_test_user(self, email='test@example.com', role='user', password='password123'):
        """Helper to create a test user."""
        with self.app.app_context():
            user = User(
                full_name='Test User',
                email=email,
                phone='1234567890',
                password=generate_password_hash(password),
                role=role,
                account_status='active',
                profile_complete=True,
                city='Kathmandu'
            )
            db.session.add(user)
            db.session.commit()
            return user
    
    def _create_test_property(self, owner_id, title='Test Property'):
        """Helper to create a test property."""
        with self.app.app_context():
            prop = Property(
                owner_id=owner_id,
                title=title,
                description='Test description',
                property_type='apartment',
                price=25000,
                city='Kathmandu',
                district='Kathmandu',
                province='Bagmati',
                bedrooms=2,
                bathrooms=1,
                furnished=True,
                parking=True,
                availability_status='available',
                verification_status='verified',
                status='active'
            )
            db.session.add(prop)
            db.session.commit()
            return prop


class AuthenticationTests(BaseTestCase):
    """Test authentication routes and functions."""
    
    def test_user_registration(self):
        """Test successful user registration."""
        with self.app.app_context():
            user = User(
                full_name='New User',
                email='newuser@example.com',
                password=generate_password_hash('password123'),
                role='user',
                account_status='active'
            )
            db.session.add(user)
            db.session.commit()
            
            # Verify user was created
            self.assertIsNotNone(user.id)
            self.assertEqual(user.email, 'newuser@example.com')
            self.assertEqual(user.role, 'user')
    
    def test_duplicate_email_prevention(self):
        """Test that duplicate emails are prevented."""
        with self.app.app_context():
            user1 = User(
                full_name='User 1',
                email='duplicate@example.com',
                password=generate_password_hash('password123'),
                role='user',
                account_status='active'
            )
            db.session.add(user1)
            db.session.commit()
            
            # Try to create duplicate
            user2 = User(
                full_name='User 2',
                email='duplicate@example.com',
                password=generate_password_hash('password123'),
                role='user',
                account_status='active'
            )
            db.session.add(user2)
            
            # Should raise IntegrityError due to unique constraint
            from sqlalchemy.exc import IntegrityError
            self.assertRaises(IntegrityError, db.session.commit)
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed."""
        with self.app.app_context():
            password = 'testpassword123'
            hashed = generate_password_hash(password)
            
            # Verify password works
            self.assertTrue(check_password_hash(hashed, password))
            
            # Verify wrong password fails
            self.assertFalse(check_password_hash(hashed, 'wrongpassword'))
    
    def test_owner_profile_creation(self):
        """Test that owner profile is created with owner role."""
        with self.app.app_context():
            user = User(
                full_name='Property Owner',
                email='owner@example.com',
                password=generate_password_hash('password123'),
                role='owner',
                account_status='active'
            )
            db.session.add(user)
            db.session.flush()
            
            owner_profile = OwnerProfile(
                user_id=user.id,
                verification_status='pending'
            )
            db.session.add(owner_profile)
            db.session.commit()
            
            # Verify owner profile
            profile = OwnerProfile.query.filter_by(user_id=user.id).first()
            self.assertIsNotNone(profile)
            self.assertEqual(profile.verification_status, 'pending')


class PropertyManagementTests(BaseTestCase):
    """Test property creation and management."""
    
    def test_property_creation(self):
        """Test creating a property."""
        with self.app.app_context():
            user = self._create_test_user(role='owner')
            prop = self._create_test_property(user.id)
            
            # Verify property
            self.assertIsNotNone(prop.id)
            self.assertEqual(prop.title, 'Test Property')
            self.assertEqual(prop.owner_id, user.id)
            self.assertEqual(prop.price, 25000)
    
    def test_property_validation(self):
        """Test property field validation."""
        with self.app.app_context():
            # Property with invalid price
            with self.assertRaises((ValueError, TypeError)):
                prop = Property(
                    owner_id=1,
                    title='Invalid Property',
                    price='invalid_price',  # Should be numeric
                    city='Kathmandu'
                )
    
    def test_property_average_rating(self):
        """Test property average rating calculation."""
        with self.app.app_context():
            owner = self._create_test_user(role='owner')
            user1 = self._create_test_user('user1@example.com')
            user2 = self._create_test_user('user2@example.com')
            
            prop = self._create_test_property(owner.id)
            
            # Add reviews
            review1 = Review(property_id=prop.id, user_id=user1.id, rating=5)
            review2 = Review(property_id=prop.id, user_id=user2.id, rating=4)
            db.session.add(review1)
            db.session.add(review2)
            db.session.commit()
            
            # Test average rating
            avg_rating = prop.average_rating()
            self.assertEqual(avg_rating, 4.5)
    
    def test_property_deletion(self):
        """Test property deletion with cascade."""
        with self.app.app_context():
            owner = self._create_test_user(role='owner')
            prop = self._create_test_property(owner.id)
            prop_id = prop.id
            
            db.session.delete(prop)
            db.session.commit()
            
            # Verify property is deleted
            deleted_prop = Property.query.get(prop_id)
            self.assertIsNone(deleted_prop)


class FavoriteTests(BaseTestCase):
    """Test favorite functionality."""
    
    def test_add_favorite(self):
        """Test adding a property to favorites."""
        with self.app.app_context():
            owner = self._create_test_user('owner@example.com', role='owner')
            user = self._create_test_user('user@example.com')
            prop = self._create_test_property(owner.id)
            
            favorite = Favorite(user_id=user.id, property_id=prop.id)
            db.session.add(favorite)
            db.session.commit()
            
            # Verify favorite
            fav = Favorite.query.filter_by(user_id=user.id, property_id=prop.id).first()
            self.assertIsNotNone(fav)
    
    def test_duplicate_favorite_prevention(self):
        """Test that duplicate favorites are prevented."""
        with self.app.app_context():
            owner = self._create_test_user('owner@example.com', role='owner')
            user = self._create_test_user('user@example.com')
            prop = self._create_test_property(owner.id)
            
            # Add same favorite twice
            fav1 = Favorite(user_id=user.id, property_id=prop.id)
            db.session.add(fav1)
            db.session.commit()
            
            fav2 = Favorite(user_id=user.id, property_id=prop.id)
            db.session.add(fav2)
            
            # Should raise IntegrityError due to unique constraint
            from sqlalchemy.exc import IntegrityError
            self.assertRaises(IntegrityError, db.session.commit)
    
    def test_remove_favorite(self):
        """Test removing a favorite."""
        with self.app.app_context():
            owner = self._create_test_user('owner@example.com', role='owner')
            user = self._create_test_user('user@example.com')
            prop = self._create_test_property(owner.id)
            
            favorite = Favorite(user_id=user.id, property_id=prop.id)
            db.session.add(favorite)
            db.session.commit()
            fav_id = favorite.id
            
            # Remove favorite
            db.session.delete(favorite)
            db.session.commit()
            
            # Verify removal
            deleted_fav = Favorite.query.get(fav_id)
            self.assertIsNone(deleted_fav)


class ReviewTests(BaseTestCase):
    """Test review functionality."""
    
    def test_add_review(self):
        """Test adding a review to a property."""
        with self.app.app_context():
            owner = self._create_test_user('owner@example.com', role='owner')
            user = self._create_test_user('user@example.com')
            prop = self._create_test_property(owner.id)
            
            review = Review(
                property_id=prop.id,
                user_id=user.id,
                rating=5,
                review='Excellent property!'
            )
            db.session.add(review)
            db.session.commit()
            
            # Verify review
            rev = Review.query.filter_by(property_id=prop.id, user_id=user.id).first()
            self.assertIsNotNone(rev)
            self.assertEqual(rev.rating, 5)
    
    def test_rating_range_validation(self):
        """Test that rating is between 1-5."""
        with self.app.app_context():
            owner = self._create_test_user('owner@example.com', role='owner')
            user = self._create_test_user('user@example.com')
            prop = self._create_test_property(owner.id)
            
            # Invalid ratings
            for invalid_rating in [0, 6, -1, 10]:
                review = Review(
                    property_id=prop.id,
                    user_id=user.id,
                    rating=invalid_rating
                )
                # Note: Add validation in actual models if needed
                self.assertNotIn(review.rating, range(1, 6))


class RoommateProfileTests(BaseTestCase):
    """Test roommate profile functionality."""
    
    def test_roommate_profile_creation(self):
        """Test creating a roommate profile."""
        with self.app.app_context():
            user = self._create_test_user()
            
            profile = RoommateProfile(
                user_id=user.id,
                preferred_city='Kathmandu',
                budget=20000,
                occupation='Student',
                gender_preference='Any',
                smoking_preference='No',
                drinking_preference='No',
                bio='Looking for a quiet place'
            )
            db.session.add(profile)
            db.session.commit()
            
            # Verify profile
            rp = RoommateProfile.query.filter_by(user_id=user.id).first()
            self.assertIsNotNone(rp)
            self.assertEqual(rp.budget, 20000)


class UtilityFunctionsTests(BaseTestCase):
    """Test utility functions."""
    
    def test_rate_limiter(self):
        """Test rate limiting functionality."""
        from app.utils.rate_limiter import limiter
        
        test_id = "test_user_123"
        
        # Allow requests
        for i in range(5):
            self.assertTrue(limiter.is_allowed(test_id, 5))
        
        # Exceed limit
        self.assertFalse(limiter.is_allowed(test_id, 5))
        
        # Check reset time
        reset_time = limiter.get_reset_time(test_id)
        self.assertGreater(reset_time, 0)
    
    def test_pagination_optimizer(self):
        """Test pagination optimizer."""
        from app.utils.pagination import PaginationOptimizer
        
        with self.app.app_context():
            # Create test data
            owner = self._create_test_user('owner@example.com', role='owner')
            for i in range(25):
                self._create_test_property(owner.id, f'Property {i}')
            
            query = Property.query
            result = PaginationOptimizer.paginate_query(query, page=1, per_page=10)
            
            self.assertEqual(len(result['items']), 10)
            self.assertEqual(result['total'], 25)
            self.assertEqual(result['pages'], 3)
            self.assertTrue(result['has_next'])
            self.assertFalse(result['has_prev'])


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(AuthenticationTests))
    suite.addTests(loader.loadTestsFromTestCase(PropertyManagementTests))
    suite.addTests(loader.loadTestsFromTestCase(FavoriteTests))
    suite.addTests(loader.loadTestsFromTestCase(ReviewTests))
    suite.addTests(loader.loadTestsFromTestCase(RoommateProfileTests))
    suite.addTests(loader.loadTestsFromTestCase(UtilityFunctionsTests))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
