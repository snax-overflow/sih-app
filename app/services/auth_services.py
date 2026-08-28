"""
Authentication Service Module.
Handles the core business logic for user registration and login.
This includes password hashing, database interactions, and JWT generation.
"""

import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import db, User

# The secret key is used to digitally sign the JWTs. 
# In a real production app, this should be hidden in a .env file!
SECRET_KEY = "super-secret-hackathon-key" 

class AuthService:
    """
    Service class that isolates authentication logic from the API routes.
    Uses @staticmethod so it can be called directly without instantiating the class.
    """

    @staticmethod
    def register_user(email, password):
        """
        Registers a new user in the database.
        
        Args:
            email (str): The user's email address.
            password (str): The user's raw, unhashed password.
            
        Returns:
            tuple: (Success dictionary, Error message if any)
        """
        # 1. Check if a user with this email already exists in the database
        if User.query.filter_by(email=email).first():
            return None, "Email already exists"
        
        # 2. Hash the password for security. 
        # NEVER save raw passwords to a database. generate_password_hash uses pbkdf2:sha256 by default.
        hashed_pw = generate_password_hash(password)
        
        # 3. Create the new User object with the hashed password
        new_user = User(email=email, password_hash=hashed_pw)
        
        # 4. Stage and commit (save) the new user to the database
        db.session.add(new_user)
        db.session.commit()
        
        return {"message": "User created successfully"}, None

    @staticmethod
    def login_user(email, password):
        """
        Verifies user credentials and issues a JSON Web Token (JWT).
        
        Args:
            email (str): The user's email address.
            password (str): The user's raw password to verify.
            
        Returns:
            tuple: (Dictionary containing the JWT, Error message if any)
        """
        # 1. Retrieve the user from the database by their email
        user = User.query.filter_by(email=email).first()
        
        # 2. Check if the user exists AND if the provided password matches the stored hash
        # check_password_hash securely compares the raw string to the hashed string
        if not user or not check_password_hash(user.password_hash, password):
            return None, "Invalid email or password"
            
        # 3. Generate a JWT Token
        # The payload contains the user's ID and an expiration time (exp) set to 24 hours from now.
        # We use timezone.utc to ensure the expiration time is consistent globally.
        token = jwt.encode({
            "user_id": user.id,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
        }, SECRET_KEY, algorithm="HS256")
        
        return {"token": token}, None