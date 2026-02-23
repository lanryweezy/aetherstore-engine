# tests/test_security.py
# Tests for security features

import pytest
from security_middleware import validate_input, sanitize_string, validate_email, validate_uuid

def test_validate_input_sql_injection():
    """Test input validation against SQL injection"""
    # Should reject SQL injection attempts
    assert not validate_input("'; DROP TABLE users; --")
    assert not validate_input("SELECT * FROM users")
    assert not validate_input("1 OR 1=1")

def test_validate_input_xss():
    """Test input validation against XSS"""
    # Should reject XSS attempts
    assert not validate_input("<script>alert('xss')</script>")
    assert not validate_input("javascript:alert('xss')")
    assert not validate_input("<iframe src='evil.com'></iframe>")

def test_validate_input_safe():
    """Test that safe inputs pass validation"""
    assert validate_input("Hello World")
    assert validate_input("Product Name 123")
    assert validate_input("user@example.com")

def test_sanitize_string():
    """Test string sanitization"""
    assert sanitize_string("Hello\x00World") == "HelloWorld"
    assert sanitize_string("  Test  ") == "Test"
    assert sanitize_string("Normal String") == "Normal String"

def test_validate_email():
    """Test email validation"""
    assert validate_email("user@example.com")
    assert validate_email("test.user@domain.co.uk")
    assert not validate_email("invalid-email")
    assert not validate_email("@example.com")
    assert not validate_email("user@")

def test_validate_uuid():
    """Test UUID validation"""
    valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
    assert validate_uuid(valid_uuid)
    assert not validate_uuid("invalid-uuid")
    assert not validate_uuid("123")
    assert not validate_uuid("")

