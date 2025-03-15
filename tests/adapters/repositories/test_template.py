import pytest
from sqlalchemy.orm import Session
from app.adapters.repositories.template import TemplateRepository
from app.adapters.persistance.template import Template


@pytest.fixture
def mock_db(mocker):
    return mocker.Mock(spec=Session)


@pytest.fixture
def template_repository(mock_db):
    return TemplateRepository(mock_db)


def test_get_by_level(template_repository, mock_db):
    # Arrange
    expected_templates = [
        Template(id=1, name="Template1", level=1),
        Template(id=2, name="Template2", level=1),
    ]
    mock_db.query.return_value.filter.return_value.all.return_value = expected_templates

    # Act
    result = template_repository.get_by_level(1)

    # Assert
    assert result == expected_templates
    mock_db.query.assert_called_once_with(Template)
    mock_db.query.return_value.filter.assert_called_once()


def test_get_by_id(template_repository, mock_db):
    # Arrange
    expected_template = Template(id=1, name="Template1", level=1)
    mock_db.query.return_value.filter.return_value.first.return_value = (
        expected_template
    )

    # Act
    result = template_repository.get_by_id(1)

    # Assert
    assert result == expected_template
    mock_db.query.assert_called_once_with(Template)
    mock_db.query.return_value.filter.assert_called_once()


def test_get_by_name(template_repository, mock_db):
    # Arrange
    expected_template = Template(id=1, name="Template1", level=1)
    mock_db.query.return_value.filter.return_value.first.return_value = (
        expected_template
    )

    # Act
    result = template_repository.get_by_name("Template1")

    # Assert
    assert result == expected_template
    mock_db.query.assert_called_once_with(Template)
    mock_db.query.return_value.filter.assert_called_once()


def test_get_by_id_not_found(template_repository, mock_db):
    # Arrange
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Act
    result = template_repository.get_by_id(999)

    # Assert
    assert result is None
    mock_db.query.assert_called_once_with(Template)
    mock_db.query.return_value.filter.assert_called_once()
