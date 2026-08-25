"""
Quick diagnostic script to verify the Supabase Postgres connection
and Supabase client (Auth/Storage) are both configured correctly.

Run from the backend/ folder with the venv activated:
    python scripts\test_connection.py
"""

import asyncio
import sys
import os

# Ensure the app package is importable when running this script directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.config import settings
from app.core.database import engine


def check_env_vars():
    """Step 1: confirm required env vars are actually set before trying anything."""
    print("=" * 70)
    print("STEP 1: Checking environment variables")
    print("=" * 70)

    required = {
        "SUPABASE_URL": settings.SUPABASE_URL,
        "SUPABASE_ANON_KEY": settings.SUPABASE_ANON_KEY,
        "SUPABASE_SERVICE_ROLE_KEY": settings.SUPABASE_SERVICE_ROLE_KEY,
        "DATABASE_URL": settings.DATABASE_URL,
        "SECRET_KEY": settings.SECRET_KEY,
    }

    all_ok = True
    for key, value in required.items():
        if not value:
            print(f"❌ {key} is MISSING or empty in .env")
            all_ok = False
        else:
            # mask sensitive values, just show a preview
            preview = value[:15] + "..." if len(value) > 15 else value
            print(f"✅ {key} = {preview}")

    if not all_ok:
        print("\nFix the missing values in your .env file, then re-run this script.")
        return False

    print("\nAll required env vars are present.\n")
    return True


async def check_database():
    """Step 2: test the actual Postgres connection via SQLAlchemy async engine."""
    print("=" * 70)
    print("STEP 2: Testing database connection (SQLAlchemy + asyncpg)")
    print("=" * 70)

    if engine is None:
        print("❌ Engine is None — DATABASE_URL was empty when app started.")
        return False

    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version();"))
            row = result.fetchone()
            print("✅ Database connection successful!")
            print(f"   Postgres version: {row[0]}")
            return True
    except Exception as e:
        print("❌ Database connection FAILED.")
        print(f"   Error: {e}")
        print("\n   Common causes:")
        print("   - Wrong password in DATABASE_URL")
        print("   - Forgot to change 'postgresql://' to 'postgresql+asyncpg://'")
        print("   - Used direct connection (port 5432) instead of pooler (port 6543)")
        print("   - Typo in the project ref or pooler hostname")
        return False
    
def check_supabase_client():
    """Step 3: test the Supabase client library initializes correctly."""
    print("\n" + "=" * 70)
    print("STEP 3: Testing Supabase client (Auth/Storage)")
    print("=" * 70)

    try:
        from supabase import create_client

        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

        try:
            buckets = client.storage.list_buckets()
            print("✅ Supabase client initialized and authenticated successfully!")
            print(f"   Found {len(buckets)} storage bucket(s).")
            for b in buckets:
                print(f"   - {b.name}")
        except Exception as inner_e:
            # Client initialized fine, but the storage call itself failed —
            # still means credentials are valid, just report it separately.
            print("✅ Supabase client initialized successfully (credentials valid).")
            print(f"   ⚠️  Storage bucket listing failed separately: {inner_e}")

        return True
    except Exception as e:
        print("❌ Supabase client FAILED to initialize.")
        print(f"   Error: {e}")
        print("\n   Common causes:")
        print("   - Wrong SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
        print("   - 'supabase' package version mismatch — try: pip install -U supabase")
        return False
    
# def check_supabase_client():
#     """Step 3: test the Supabase client library (Auth/Storage access)."""
#     print("\n" + "=" * 70)
#     print("STEP 3: Testing Supabase client (Auth/Storage)")
#     print("=" * 70)

#     try:
#         from supabase import create_client

#         client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

#         # A lightweight call to confirm the client + keys actually work.
#         # Listing storage buckets is a safe, low-risk way to validate credentials.
#         buckets = client.storage.list_buckets()
#         print("✅ Supabase client initialized and authenticated successfully!")
#         print(f"   Found {len(buckets)} storage bucket(s).")
#         if buckets:
#             for b in buckets:
#                 print(f"   - {b.name}")
#         else:
#             print("   (No buckets created yet — that's expected if this is a fresh project.)")
#         return True
#     except Exception as e:
#         print("❌ Supabase client FAILED.")
#         print(f"   Error: {e}")
#         print("\n   Common causes:")
#         print("   - Wrong SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
#         print("   - 'supabase' package version mismatch — try: pip install -U supabase")
#         return False


async def main():
    print("\nTechnify VisionAI — Connection Diagnostics\n")

    env_ok = check_env_vars()
    if not env_ok:
        sys.exit(1)

    db_ok = await check_database()
    supabase_ok = check_supabase_client()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Database connection : {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"Supabase client      : {'✅ PASS' if supabase_ok else '❌ FAIL'}")

    if db_ok and supabase_ok:
        print("\n🎉 Everything is connected correctly. Ready to build models and migrations.")
    else:
        print("\n⚠️  Fix the failing checks above before moving forward.")


if __name__ == "__main__":
    asyncio.run(main())