"""Initial data migration

Revision ID: 001
Revises: 
Create Date: 2023-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from app.models.material import MaterialType
from app.models.user import User
from app.database import Base
import os

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    # Create all tables from models
    Base.metadata.create_all(bind=bind)
    
    session = sa.orm.Session(bind=bind)

    # Insert initial user
    user = User(
        user_id="1",
        email="admin@localhost",
        hashed_password="2131lk",
    )

    level_types = [
        "Text Notes",
        "Receipts and Bills",
        "Sketches and Drawings",
        "Whiteboard Photos",
        "Screenshots",
        "Forms and Checklists",
        "Medical Documents",
        "Miscellaneous",
    ]
    level_types = [d.lower().replace(" ", "_") for d in level_types]

    # Insert level 0 material types
    material_types = [
        MaterialType(id=i, name=name, description="", level=0)
        for i, name in enumerate(level_types)
    ]
    session.add_all(material_types)
    
    # Insert level 1 material types from schema files
    schema_path = "app/material_schema/lv2"
    lv1_folder = os.listdir(schema_path)
    for folder in lv1_folder:
        try:
            lv1_id = level_types.index(folder)
        except ValueError:
            continue
            
        files = os.listdir(f"{schema_path}/{folder}")
        for fname in files:
            schema_name = f"{folder} > {fname}"
            schema = open(os.path.join(f"{schema_path}/{folder}", fname)).read()
            material_type = MaterialType(
                name=schema_name,
                description="",
                schema=schema,
                level=1,
                parent_id=lv1_id,
            )
            session.add(material_type)

    session.add(user)
    session.commit()

def downgrade() -> None:
    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)
    
    # Delete all data first
    session.query(MaterialType).delete()
    session.query(User).delete()
    session.commit()

    # Drop all tables
    Base.metadata.drop_all(bind=bind)
