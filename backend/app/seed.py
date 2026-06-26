"""
Database Seeder — creates a predefined demo user for testing.

Usage:
    python -m app.seed
    python -m app.seed --username admin --password admin123
"""
import asyncio
import argparse
from datetime import datetime, timezone

from app.database import connect_db, close_db, get_users_collection
from app.services.auth import hash_password


DEMO_USER = {
    "email": "demo@hematoscan.com",
    "username": "demo",
    "password": "demo123",
    "full_name": "Demo User",
}


async def seed_user(
    username: str = DEMO_USER["username"],
    email: str = DEMO_USER["email"],
    password: str = DEMO_USER["password"],
    full_name: str = DEMO_USER["full_name"],
):
    """Create or update a predefined user."""
    await connect_db()
    users = await get_users_collection()

    existing = await users.find_one({"$or": [{"email": email}, {"username": username}]})

    if existing:
        print(f"⚠️  User '{username}' already exists (email: {existing['email']})")
        print(f"   Updating password...")

        await users.update_one(
            {"_id": existing["_id"]},
            {
                "$set": {
                    "hashed_password": hash_password(password),
                    "full_name": full_name,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )
        print(f"✅ User '{username}' password updated successfully!")
    else:
        user_doc = {
            "email": email,
            "username": username,
            "hashed_password": hash_password(password),
            "full_name": full_name,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        result = await users.insert_one(user_doc)
        print(f"✅ Demo user '{username}' created! (id: {result.inserted_id})")

    print(f"\n📋 Login credentials:")
    print(f"   Username/Email: {username} / {email}")
    print(f"   Password:       {password}")

    await close_db()


def main():
    parser = argparse.ArgumentParser(description="Seed predefined demo user")
    parser.add_argument("--username", default=DEMO_USER["username"])
    parser.add_argument("--email", default=DEMO_USER["email"])
    parser.add_argument("--password", default=DEMO_USER["password"])
    parser.add_argument("--full-name", default=DEMO_USER["full_name"])
    args = parser.parse_args()

    asyncio.run(seed_user(
        username=args.username,
        email=args.email,
        password=args.password,
        full_name=args.full_name,
    ))


if __name__ == "__main__":
    main()
