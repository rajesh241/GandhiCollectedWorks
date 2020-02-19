"""Unit Test module for User App"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
USER_URL = reverse('user:user_api_view')
TOKEN_URL = reverse('user:token_obtain_pair')
ME_URL = reverse('user:me')


def create_user(**params):
    """Create User Function"""
    return get_user_model().objects.create_user(**params)

def create_super_user(**params):
    """Create User Function"""
    return get_user_model().objects.create_superuser(**params)

class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            'email': 'test@londonappdev.com',
            'password': 'testpass',
            'password2': 'testpass',
            'name': 'Test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        user_id = res.data.get('id')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(id=user_id)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creatinga  user that already exists fails"""
        payload = {'email': 'test@londonappdev.com', 'password': 'testpass'}
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters"""
        payload = {'email': 'test@londonappdev.com', 'password': 'pw'}
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {'email': 'test@londonappdev.com', 'password': 'testpass'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('access', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(email='test@londonappdev.com', password="testpass")
        payload = {'email': 'test@londonappdev.com', 'password': 'wrong'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exist"""
        payload = {'email': 'test@londonappdev.com', 'password': 'testpass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class ClientUserApiTests(TestCase):
    """Test case for the client role"""
    def setUp(self):
        self.user = create_user(
            email='test@londonappdev.com',
            password='testpass',
            name='rajesh'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    def test_retrieve_user_list_fail(self):
        """Retrieving the user list for client role should fail"""
        res = self.client.get(USER_URL)
        print(res.status_code)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

class StaffUserApiTests(TestCase):
    """Test case for the realtor role"""
    def setUp(self):
        
        self.admin = create_super_user(
            email='admin@admin.com',
            password='testpass',
        )

        self.user = create_user(
            email='staff@staff.com',
            password='testpass',
            name='staff'
        )
        self.user.is_staff = True
        self.user.save()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_list_success(self):
        """Retrieving the user list for staff role"""
        res = self.client.get(USER_URL)
        data = res.json()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get('count'), 1)

    def test_retrieve_admin_user_fail(self):
        """Retrieving the admin user for staff role"""
        res = self.client.get(f"{USER_URL}?id={self.admin.id}")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_nonadmin_user_pass(self):
        """Retrieving the admin user for staff role"""
        res = self.client.get(f"{USER_URL}?id={self.user.id}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_user_edit(self):
        """Testing the user edit, it should allow all fields"""
        new_name = "staff_name_changed"
        header = {'content-type' : 'application/json'}
        patch_data = { 'name' : new_name, 'is_superuser' : 1}
        res = self.client.patch(f"{USER_URL}?id={self.user.id}", data=patch_data)
        data = res.json()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get('name'), new_name)
        self.assertEqual(data.get('is_superuser'), 0)

    def test_admin_delete(self):
        """Should not be able to delete admin"""
        res = self.client.delete(f"{USER_URL}?id={self.admin.id}")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_user_delete(self):
        """Should be able to delete the user"""
        res = self.client.delete(f"{USER_URL}?id={self.user.id}")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        print("should be able to delete")

class AdminUserApiTests(TestCase):
    """Test case for the admin role"""
    def setUp(self):
        
        self.admin = create_super_user(
            email='admin@admin.com',
            password='testpass',
        )

        self.user = create_user(
            email='staff@staff.com',
            password='testpass',
            name='staff'
        )
        self.user.is_staff = True
        self.user.save()
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_retrieve_user_list_success(self):
        """Retrieving the user list for staff role"""
        res = self.client.get(USER_URL)
        print(res.status_code)
        print(res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_admin_user_fail(self):
        """Retrieving the admin user for staff role"""
        res = self.client.get(f"{USER_URL}?id={self.admin.id}")
        print(res.status_code)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_user_edit(self):
        """Testing the user edit, it should allow all fields"""
        new_name = "staff_name_changed"
        header = {'content-type' : 'application/json'}
        patch_data = { 'name' : new_name, 'is_superuser' : 1}
        res = self.client.patch(f"{USER_URL}?id={self.user.id}", data=patch_data)
        data = res.json()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get('name'), new_name)
        self.assertEqual(data.get('is_superuser'), 1)

    def test_admin_delete(self):
        """Should not be able to delete admin"""
        res = self.client.delete(f"{USER_URL}?id={self.admin.id}")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)



class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@londonappdev.com',
            password='testpass',
            name='rajesh'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in used"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get('name'), self.user.name)
        self.assertEqual(res.data.get('email'), self.user.email)
       #self.assertEqual(res.data, {
       #    'name': self.user.name,
       #    'email': self.user.email
       #})

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me url"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {'name': 'new name', 'password': 'newpassword123',
                   'password2':'newpassword123'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
