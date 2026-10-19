"""Crea el usuario administrador inicial y, opcionalmente, su organización."""

import argparse

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.identity import Organization, Role, User, user_organization_roles


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--organization", default="AndroScan Demo")
    parser.add_argument("--slug", default="androscan-demo")
    args = parser.parse_args()

    with SessionLocal() as db:
        email = args.email.strip().lower()
        if db.scalar(select(User).where(User.email == email)):
            raise SystemExit("El usuario ya existe.")

        admin_role = db.scalar(select(Role).where(Role.name == "ADMIN"))
        if not admin_role:
            raise SystemExit("Ejecute las migraciones antes de crear el administrador.")

        organization = db.scalar(select(Organization).where(Organization.slug == args.slug))
        if not organization:
            organization = Organization(name=args.organization, slug=args.slug)
            db.add(organization)
            db.flush()

        user = User(email=email, full_name=args.name, password_hash=hash_password(args.password))
        db.add(user)
        db.flush()
        db.execute(
            user_organization_roles.insert().values(
                user_id=user.id,
                organization_id=organization.id,
                role_id=admin_role.id,
            )
        )
        db.commit()
        print(f"Administrador creado: {email}")
        print(f"Organización: {organization.name} ({organization.slug})")


if __name__ == "__main__":
    main()
