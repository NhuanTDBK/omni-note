import os
import json

from app.db.database import get_db
from app.models.base import Base
from app.models.material import MaterialType
from app.models.user import User


def init_db():
    """Initialize database connection and create tables."""
    session = get_db()
    # Create all tables
    Base.metadata.create_all(session.bind)

    # insert user 1 to user table
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
        # "Bookmarks and Clippings",
        "Forms and Checklists",
        "Medical Documents",
        "Miscellaneous",
    ]
    level_types = [d.lower().replace(" ", "_") for d in level_types]

    material_types = [
        MaterialType(id=i, name=name, description="", level=0)
        for i, name in enumerate(level_types)
    ]

    # Check app/material_schema, and automatically insert the schema into the database
    schema_path = "app/material_schema/lv2"
    lv1_folder = os.listdir(schema_path)
    for folder in lv1_folder:

        lv1_id = level_types.index(folder)
        if lv1_id == -1:
            continue
        files = os.listdir(f"{schema_path}/{folder}")
        for fname in files:
            schema_name = f"{folder} > {fname}"
            schema = open(os.path.join(f"{schema_path}/{folder}"), fname).read()
            material_type = MaterialType(
                name=schema_name,
                description="",
                schema=schema,
                level=1,
                parent_id=lv1_id,
            )
            session.add(material_type)
            try:
                session.commit()
                print(f"Insert schema {schema_name}")
            except Exception as e:
                print(e)
                session.rollback()

    session.add(user)
    try:
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()


if __name__ == "__main__":
    init_db()
