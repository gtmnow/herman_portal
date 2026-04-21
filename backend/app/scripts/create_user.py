import argparse
from datetime import datetime

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.auth_user import AuthUser
from app.models.auth_user_credential import AuthUserCredential


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or update a Herman Portal auth user.")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--user-id-hash", required=True)
    parser.add_argument("--display-name", default=None)
    parser.add_argument("--tenant-id", default="tenant_demo")
    parser.add_argument("--admin", action="store_true")
    args = parser.parse_args()

    session = SessionLocal()
    try:
        normalized_email = args.email.strip().lower()
        user = session.execute(select(AuthUser).where(AuthUser.email == normalized_email)).scalar_one_or_none()
        if user is None:
            user = AuthUser(
                email=normalized_email,
                user_id_hash=args.user_id_hash,
                display_name=args.display_name,
                tenant_id=args.tenant_id,
                is_admin=args.admin,
            )
            session.add(user)
        else:
            user.user_id_hash = args.user_id_hash
            user.display_name = args.display_name
            user.tenant_id = args.tenant_id
            user.is_admin = args.admin
            user.updated_at = datetime.utcnow()
            session.add(user)

        credentials = session.get(AuthUserCredential, args.user_id_hash)
        if credentials is None:
            credentials = AuthUserCredential(user_id_hash=args.user_id_hash)
        credentials.password_hash = hash_password(args.password)
        credentials.password_algorithm = "bcrypt"
        credentials.password_set_at = datetime.utcnow()
        credentials.failed_login_attempts = 0
        credentials.locked_until = None
        session.add(credentials)

        session.commit()
        print(f"User ready: {normalized_email}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
