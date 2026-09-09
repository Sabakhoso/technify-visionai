import os

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

supabase = create_client(url, key)

email = input("Enter Supabase user email: ")
password = input("Enter Supabase user password: ")

response = supabase.auth.sign_in_with_password(
    {
        "email": email,
        "password": password,
    }
)

session = response.session

if session:
    print("\nAccess token:")
    print(session.access_token)
else:
    print("\nLogin failed.")
    print(response)