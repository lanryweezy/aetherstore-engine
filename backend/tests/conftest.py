# tests/conftest.py
# Pytest configuration and fixtures

import pytest
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test environment variables
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["STRIPE_SECRET_KEY"] = "sk_test_fake"
os.environ["PAYSTACK_SECRET_KEY"] = "sk_test_fake"

@pytest.fixture(scope="session")
def test_app():
    """Create test application"""
    from main_app import app
    return app

@pytest.fixture
def test_client(test_app):
    """Create test client"""
    from fastapi.testclient import TestClient
    return TestClient(test_app)

