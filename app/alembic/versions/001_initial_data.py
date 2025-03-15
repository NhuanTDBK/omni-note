"""Initial data migration

Revision ID: 001
Revises:
Create Date: 2023-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

from app.adapters.persistance.base import Base
from app.adapters.persistance.user import User
from app.adapters.persistance.material import MaterialContent
from app.adapters.persistance.template import Template
from app.adapters.persistance.tag import Tag
from sqlalchemy.schema import MetaData


# revision identifiers
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    # Create all tables from models
    metadata: MetaData = Base.metadata
    metadata.create_all(bind=bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)

    # Delete all data first
    metadata = Base.metadata
    
    # Drop tables explicitly in reverse order of dependencies
    for table in reversed(metadata.sorted_tables):
        op.drop_table(table.name)

    session.commit()

    # Drop all tables
    Base.metadata.drop_all(bind=bind)
