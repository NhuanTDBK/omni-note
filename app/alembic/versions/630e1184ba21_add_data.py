"""add data

Revision ID: 630e1184ba21
Revises: 001
Create Date: 2025-03-15 15:06:31.397864

"""

from typing import Union, Sequence
import os
from alembic import op
import sqlalchemy as sa
from app.adapters.persistance.user import User
from app.adapters.persistance.template import Template


# revision identifiers, used by Alembic.
revision: str = "630e1184ba21"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
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
        Template(id=i, name=name, description="", level=1)
        for i, name in enumerate(level_types)
    ]

    # Keep track of the last used ID
    current_id = len(level_types)

    # Insert level 1 material types from schema files
    schema_path = "material_schema/lv2"
    lv1_folder = os.listdir(schema_path)
    for folder in lv1_folder:
        try:
            lv1_id = level_types.index(folder)
        except ValueError:
            continue

        files = os.listdir(f"{schema_path}/{folder}")
        for fname in files:
            fname = fname.replace(".json", "")
            schema_name = f"{folder} > {fname}"
            schema = open(os.path.join(f"{schema_path}/{folder}", fname)).read()
            material_type = Template(
                id=current_id,
                name=schema_name,
                description="",
                schema=schema,
                level=2,
                parent_id=lv1_id,
            )
            current_id += 1
            material_types.append(material_type)

    session.add_all(material_types)
    session.add(user)
    session.commit()


def downgrade() -> None:
    pass
