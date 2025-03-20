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

    def create(self, template: Template) -> Template:
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template

    def update(self, template: Template) -> Template:
        existing_template = self.get_by_id(template.id)
        if not existing_template:
            return None
        for key, value in template.__dict__.items():
            if key != '_sa_instance_state':
                setattr(existing_template, key, value)
        self.db.commit()
        self.db.refresh(existing_template)
        return existing_template

    def delete(self, template_id: int) -> bool:
        template = self.get_by_id(template_id)
        if not template:
            return False
        self.db.delete(template)
        self.db.commit()
        return True
