"""
Creates a Supabase-authenticated admin user, tagged with the app_metadata
(organization_id, app_role) that app/core/security.py trusts on every
request — and creates the organization row too if you don't have one yet.

Run from the backend/ folder with the venv activated:
    python scripts\create_admin.py --email admin@technify.dev --password ChangeMe123! --org-name "Technify HQ"

To attach the user to an org you already have instead of creating one:
    python scripts\create_admin.py --email admin@technify.dev --password ChangeMe123! --org-id <existing-uuid>
"""

import argparse
import asyncio
import os
import re
import sys
import uuid

# Ensure the app package is importable when running this script directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.integrations.supabase_client import admin_create_user
from app.models.organization import Organization


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    return slug or f"org-{uuid.uuid4().hex[:8]}"


async def _get_or_create_organization(*, org_id: str | None, org_name: str | None) -> Organization:
    async with AsyncSessionLocal() as session:
        if org_id:
            result = await session.execute(select(Organization).where(Organization.id == org_id))
            organization = result.scalar_one_or_none()
            if organization is None:
                raise SystemExit(f"No organization found with id={org_id}")
            return organization

        slug = _slugify(org_name)
        result = await session.execute(select(Organization).where(Organization.slug == slug))
        existing = result.scalar_one_or_none()
        if existing is not None:
            print(f"Using existing organization '{existing.name}' ({existing.id})")
            return existing

        organization = Organization(name=org_name, slug=slug)
        session.add(organization)
        await session.commit()
        await session.refresh(organization)
        print(f"Created organization '{organization.name}' ({organization.id})")
        return organization


async def main() -> None:
    parser = argparse.ArgumentParser(description="Create a Supabase admin user for Technify VisionAI")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True, help="Min 6 characters — Supabase's own requirement")
    parser.add_argument("--role", default="admin", help="app_role stored in app_metadata (default: admin)")
    org_group = parser.add_mutually_exclusive_group(required=True)
    org_group.add_argument("--org-name", help="Creates this organization if it doesn't already exist")
    org_group.add_argument("--org-id", help="Attaches the user to an existing organization by UUID")
    args = parser.parse_args()

    organization = await _get_or_create_organization(org_id=args.org_id, org_name=args.org_name)

    user = await admin_create_user(
        email=args.email,
        password=args.password,
        email_confirm=True,
        organization_id=organization.id,
        app_role=args.role,
    )

    print("\nAdmin user created successfully:")
    print(f"  email:           {user['email']}")
    print(f"  user_id:         {user['id']}")
    print(f"  organization_id: {organization.id}")
    print(f"  app_role:        {args.role}")
    print("\nLog in with this email/password in the frontend's /login page.")


if __name__ == "__main__":
    asyncio.run(main())