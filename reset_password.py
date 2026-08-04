"""
Script to reset all non-admin user passwords to 'admin123'.
Skips all accounts with role == 'admin'.

Run with: python reset_passwords.py
"""

from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User

# Initialize the Flask application using your app factory
app = create_app()

def reset_non_admin_passwords(new_password="admin123"):
    with app.app_context():
        # Generate the Werkzeug hash for the target password
        hashed_password = generate_password_hash(new_password)

        # Query all users where role is NOT 'admin'
        non_admin_users = User.query.filter(User.role != 'admin').all()

        if not non_admin_users:
            print("❌ No non-admin users found in the database.")
            return

        # Update passwords for all matching users
        count = 0
        for user in non_admin_users:
            user.password = hashed_password
            count += 1

        # Commit all changes to the database
        db.session.commit()
        print(
            f"✅ Successfully updated {count} non-admin user(s) to '{new_password}'.\n"
            f"🛡️  All admin accounts were safely left untouched."
        )

if __name__ == "__main__":
    reset_non_admin_passwords()