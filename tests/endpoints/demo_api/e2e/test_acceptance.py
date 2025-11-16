"""
Acceptance tests for demo_api endpoint.

Tests the acceptance criteria defined in v0.1.0.md (AT-001 to AT-004).
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(test_app):
    """
    Provide a test client for the FastAPI application.

    Args:
        test_app: FastAPI application fixture.

    Yields:
        TestClient instance.
    """
    return TestClient(test_app)


class TestAcceptanceCriteria:
    """Acceptance test suite matching v0.1.0 requirements."""

    @pytest.mark.e2e
    def test_at001_health_check_via_api(self, client):
        """
        AT-001: Health Check.

        Étant donné que l'application est démarrée,
        Lorsque le client appelle GET /health,
        Alors la réponse doit être 200 OK avec un payload indiquant que le service est "UP".
        """
        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "UP"

    @pytest.mark.e2e
    def test_at002_create_demo_item(self, client):
        """
        AT-002: Création.

        Étant donné que PostgreSQL est accessible et que la table demo_items existe,
        Lorsque le client appelle POST /demo-items avec un label valide,
        Alors un enregistrement est créé dans PostgreSQL,
        Et la réponse contient l'id généré et le label,
        Et le code HTTP est 201 Created.
        """
        # Arrange
        payload = {"label": "Test Item"}

        # Act
        response = client.post("/demo-items", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["label"] == "Test Item"
        assert "created_at" in data

    @pytest.mark.e2e
    def test_at003_list_demo_items(self, client):
        """
        AT-003: Lecture.

        Étant donné qu'au moins un demo_item existe,
        Lorsque le client appelle GET /demo-items,
        Alors la réponse retourne la liste des éléments,
        Et le code HTTP est 200 OK.
        """
        # Arrange - Create items
        client.post("/demo-items", json={"label": "Item 1"})
        client.post("/demo-items", json={"label": "Item 2"})

        # Act
        response = client.get("/demo-items")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
