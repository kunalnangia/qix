import psycopg2
from datetime import datetime, timezone
from passlib.hash import bcrypt
import uuid

def add_auth_user():
    print("Adding test user to auth.users...")
    
    # Test user details
    user_email = "test@example.com"
    user_password = "test1234"
    user_id = str(uuid.uuid4())
    
    # Hash the password
    hashed_password = bcrypt.hash(user_password)
    
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host="db.lflecyuvttemfoyixngi.supabase.co",
            database="postgres",
            user="postgres",
            password="Ayeshaayesha12@",
            port="5432"
        )
        
        # Set autocommit to True to avoid transaction issues
        conn.autocommit = True
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("""
            SELECT id FROM auth.users WHERE email = %s;
        """, (user_email,))
        
        existing_user = cursor.fetchone()
        
        if existing_user:
            print(f"❌ User already exists with ID: {existing_user[0]}")
            return False
        
        # Insert the test user into auth.users
        cursor.execute("""
            INSERT INTO auth.users (
                id, instance_id, aud, role, email, encrypted_password, 
                email_confirmed_at, invited_at, confirmation_token, 
                confirmation_sent_at, recovery_token, recovery_sent_at, 
                email_change_token_new, email_change, email_change_sent_at, 
                last_sign_in_at, raw_app_meta_data, raw_user_meta_data, 
                is_super_admin, is_sso_user, 
                created_at, updated_at, phone, phone_confirmed_at, 
                phone_change, phone_change_token, phone_change_sent_at, 
                email_change_token_current, email_change_confirm_status, 
                banned_until, reauthentication_token, reauthentication_sent_at, 
                is_anonymous
            ) VALUES (
                %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, 
                %s, %s, %s, 
                %s, %s, %s, 
                %s, %s, %s, 
                %s, %s, 
                %s, %s, %s, %s, 
                %s, %s, %s, 
                %s, %s, 
                %s, %s, %s, 
                %s
            )
        """, (
            user_id,  # id
            '00000000-0000-0000-0000-000000000000',  # instance_id
            'authenticated',  # aud
            'authenticated',  # role
            user_email,  # email
            hashed_password,  # encrypted_password
            datetime.now(timezone.utc),  # email_confirmed_at
            None,  # invited_at
            '',  # confirmation_token
            None,  # confirmation_sent_at
            '',  # recovery_token
            None,  # recovery_sent_at
            '',  # email_change_token_new
            '',  # email_change
            None,  # email_change_sent_at
            None,  # last_sign_in_at
            '{"provider": "email", "providers": ["email"]}',  # raw_app_meta_data
            '{}',  # raw_user_meta_data
            False,  # is_super_admin
            False,  # is_sso_user
            datetime.now(timezone.utc),  # created_at
            datetime.now(timezone.utc),  # updated_at
            None,  # phone
            None,  # phone_confirmed_at
            '',  # phone_change
            '',  # phone_change_token
            None,  # phone_change_sent_at
            '',  # email_change_token_current
            0,  # email_change_confirm_status
            None,  # banned_until
            '',  # reauthentication_token
            None,  # reauthentication_sent_at
            False  # is_anonymous
        ))
        
        print(f"✅ Successfully added test user with ID: {user_id}")
        print(f"Email: {user_email}")
        print(f"Password: {user_password}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding test user: {str(e)}")
        return False
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    add_auth_user()
