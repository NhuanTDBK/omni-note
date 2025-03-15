from typing import List
from sqlalchemy.orm import Session
from app.adapters.persistance.template import Template


class TemplateRepository:
    def __init__(self, db: Session = None):
        self.db = db

    def get_by_level(self, level: int) -> List[Template]:
        return self.db.query(Template).filter(Template.level == level).all()

    def get_by_id(self, id: int) -> Template:
        """
        Get a template by its ID
        Args:
            id: The ID of the template
        Returns:
            The template with the specified ID

        Exceptions:
            - If no template with the specified ID is found, return None

        """
        # check empty result
        return self.db.query(Template).filter(Template.id == id).first()

    def get_by_name(self, name: str) -> Template:
        """
        Get a template by its name
        Args:
            name: The name of the template
        Returns:
            The template with the specified name

        Exceptions:
            - If no template with the specified name is found, return None

        """
        # check empty result
        return self.db.query(Template).filter(Template.name == name).first()

    def get_by_parent_id(self, parent_id: int) -> List[Template]:
        return self.db.query(Template).filter(Template.parent_id == parent_id).all()
