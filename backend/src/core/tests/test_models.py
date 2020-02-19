"""
Implementing Tests for the Core Module
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """
    Tests for testing core Models
    """
    def test_create_user_with_email_successful(self):
        """Testing creating of user with email and password"""
        email = "testuser@gmail.com"
        password = "test123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email of the new user is normalized"""
        email = 'testuser@GMAIL.COM'
        user = get_user_model().objects.create_user(
            email=email,
            password='abcd',
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Tests if the user email is valid"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=None,
                password='133'
            )

    def test_create_new_superuser(self):
        """Test creating a new super user"""
        user = get_user_model().objects.create_superuser(
            'abcd.com', 'abcd'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
