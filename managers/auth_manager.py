import psycopg2
import re
import hashlib
import os

class AuthManager:
    def __init__(self):
        self.conn_params = {
            'dbname': 'finalquiztasy',
            'user': 'postgres',
            'password': '1234',
            'host': 'localhost',
            'port': '5432'
        }
        self.current_user = None
        self.init_database()

    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        try:
            conn = psycopg2.connect(**self.conn_params)
            cursor = conn.cursor()

            # Create users table if it doesn't exist
            cursor.execute('''CREATE TABLE IF NOT EXISTS users
            (
                id
                SERIAL
                PRIMARY
                KEY,
                email
                VARCHAR
                              (
                255
                              )
                UNIQUE NOT NULL,password_hash VARCHAR
                              (
                                  255
                              ) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

            # Create player_stats table for game progress and stats
            cursor.execute(''' CREATE TABLE IF NOT EXISTS player_stats
            (
                user_id
                INTEGER
                PRIMARY
                KEY
                REFERENCES
                users
                               (
                id
                               ),
                level INTEGER DEFAULT 1,
                score INTEGER DEFAULT 0,
                completed_quizzes TEXT[],
                last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

            conn.commit()
            cursor.close()
            conn.close()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Database initialization error: {e}")

    def _hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def validate_email(self, email):
        """Validate email format using regex"""
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(email_pattern, email) is not None

    def validate_password(self, password):
        """Validate password meets minimum requirements"""
        # Password must be at least 6 characters long
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        return True, "Password is valid"

    def check_email_exists(self, email):
        """Check if an email already exists in the database"""
        try:
            conn = psycopg2.connect(**self.conn_params)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            result = cursor.fetchone() is not None
            cursor.close()
            conn.close()
            return result
        except Exception as e:
            print(f"Database error checking email: {e}")
            return False

    def register(self, email, password):
        """
        Register a new user

        Args:
            email (str): User's email address
            password (str): User's password

        Returns:
            tuple: (success, message)
        """
        # Validate email format
        if not self.validate_email(email):
            return False, "Invalid email format"

        # Validate password requirements
        valid_password, password_message = self.validate_password(password)
        if not valid_password:
            return False, password_message

        try:
            conn = psycopg2.connect(**self.conn_params)
            cursor = conn.cursor()

            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return False, "Email already registered"

            # Insert new user
            hashed_password = self._hash_password(password)
            cursor.execute(
                "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id",
                (email, hashed_password)
            )
            user_id = cursor.fetchone()[0]

            # Initialize player stats
            cursor.execute(
                "INSERT INTO player_stats (user_id) VALUES (%s)",
                (user_id,)
            )

            conn.commit()
            cursor.close()
            conn.close()
            return True, "Registration successful"
        except Exception as e:
            print(f"Registration error: {e}")
            return False, f"Registration failed: {str(e)}"

    def login(self, email, password):
        """
        Login user with email and password

        Args:
            email (str): User's email address
            password (str): User's password

        Returns:
            tuple: (success, message)
        """
        try:
            conn = psycopg2.connect(**self.conn_params)
            cursor = conn.cursor()

            hashed_password = self._hash_password(password)
            cursor.execute(
                "SELECT id, email FROM users WHERE email = %s AND password_hash = %s",
                (email, hashed_password)
            )
            user = cursor.fetchone()

            if user:
                self.current_user = {"id": user[0], "email": user[1]}

                # Update last login time
                cursor.execute(
                    "UPDATE player_stats SET last_login = CURRENT_TIMESTAMP WHERE user_id = %s",
                    (user[0],)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return True, "Login successful"
            else:
                cursor.close()
                conn.close()
                return False, "Invalid email or password"
        except Exception as e:
            print(f"Login error: {e}")
            return False, f"Login failed: {str(e)}"

    def logout(self):
        """Logout current user"""
        self.current_user = None
        return True, "Logged out successfully"

    def get_current_user(self):
        """Get current logged in user"""
        return self.current_user

    def get_user_stats(self):
        """Get stats for the current user"""
        if not self.current_user:
            return None

        try:
            conn = psycopg2.connect(**self.conn_params)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT level, score, completed_quizzes FROM player_stats WHERE user_id = %s",
                (self.current_user["id"],)
            )
            stats = cursor.fetchone()

            cursor.close()
            conn.close()

            if stats:
                return {
                    "level": stats[0],
                    "score": stats[1],
                    "completed_quizzes": stats[2] if stats[2] else []
                }
            return None
        except Exception as e:
            print(f"Error fetching user stats: {e}")
            return None