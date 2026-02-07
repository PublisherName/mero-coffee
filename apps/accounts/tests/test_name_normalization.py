from django.contrib.auth import get_user_model

from apps.accounts.models import KYC

from .base import BaseTestCase

User = get_user_model()


class NameFieldNormalizationTests(BaseTestCase):
    """Test suite for name field normalization (first_name, last_name, full_name, etc.)"""

    # ========== User Model - First Name & Last Name Tests ==========

    def test_user_first_name_normalized_to_title_case(self):
        """Test that first_name is normalized to title case"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            first_name="john",
            last_name="doe",
            password="testpass123",
        )
        self.assertEqual(user.first_name, "John")

    def test_user_last_name_normalized_to_title_case(self):
        """Test that last_name is normalized to title case"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            first_name="john",
            last_name="doe",
            password="testpass123",
        )
        self.assertEqual(user.last_name, "Doe")

    def test_user_names_with_uppercase_normalized(self):
        """Test that uppercase names are normalized to title case"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            first_name="JOHN",
            last_name="DOE",
            password="testpass123",
        )
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")

    def test_user_names_with_mixed_case_normalized(self):
        """Test that mixed case names are normalized to title case"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            first_name="jOhN",
            last_name="dOe",
            password="testpass123",
        )
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")

    def test_user_names_with_whitespace_trimmed(self):
        """Test that leading/trailing whitespace is removed"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            first_name="  john  ",
            last_name="  doe  ",
            password="testpass123",
        )
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")

    def test_user_multi_word_names_normalized(self):
        """Test that multi-word names are properly title cased"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            first_name="mary jane",
            last_name="van der berg",
            password="testpass123",
        )
        self.assertEqual(user.first_name, "Mary Jane")
        self.assertEqual(user.last_name, "Van Der Berg")

    # ========== KYC Model - Full Name, Address, ID Number Tests ==========

    def test_kyc_full_name_normalized_to_title_case(self):
        """Test that KYC full_name is normalized to title case"""
        user = self.create_user()
        kyc = KYC.objects.create(
            user=user,
            full_name="john doe smith",
            phone="1234567890",
            address="123 main street",
            id_number="abc123",
        )
        self.assertEqual(kyc.full_name, "John Doe Smith")

    def test_kyc_full_name_uppercase_normalized(self):
        """Test that uppercase full_name is normalized"""
        user = self.create_user()
        kyc = KYC.objects.create(
            user=user,
            full_name="JOHN DOE SMITH",
            phone="1234567890",
            address="123 main street",
            id_number="abc123",
        )
        self.assertEqual(kyc.full_name, "John Doe Smith")

    def test_kyc_full_name_whitespace_trimmed(self):
        """Test that full_name whitespace is trimmed"""
        user = self.create_user()
        kyc = KYC.objects.create(
            user=user,
            full_name="  john doe  ",
            phone="1234567890",
            address="123 main street",
            id_number="abc123",
        )
        self.assertEqual(kyc.full_name, "John Doe")

    def test_kyc_address_normalized_to_capitalize(self):
        """Test that address segments are title cased after commas"""
        user = self.create_user()
        kyc = KYC.objects.create(
            user=user,
            full_name="John Doe",
            phone="1234567890",
            address="123 main street, apartment 4B, building c",
            id_number="abc123",
        )
        self.assertEqual(kyc.address, "123 Main Street, Apartment 4B, Building C")

    def test_kyc_address_uppercase_normalized(self):
        """Test that uppercase address is normalized"""
        user = self.create_user()
        kyc = KYC.objects.create(
            user=user,
            full_name="John Doe",
            phone="1234567890",
            address="123 MAIN STREET, APT 5",
            id_number="abc123",
        )
        self.assertEqual(kyc.address, "123 Main Street, Apt 5")

    def test_kyc_address_whitespace_trimmed(self):
        """Test that address whitespace is trimmed"""
        user = self.create_user()
        kyc = KYC.objects.create(
            user=user,
            full_name="John Doe",
            phone="1234567890",
            address="  123 main street  ",
            id_number="abc123",
        )
        self.assertEqual(kyc.address, "123 Main Street")

    def test_kyc_address_multi_segment_normalized(self):
        """Test that multi-segment addresses are properly normalized"""
        user = self.create_user()
        kyc = KYC.objects.create(
            user=user,
            full_name="John Doe",
            phone="1234567890",
            address="123 main street, apartment 4b, new york, ny 10001",
            id_number="abc123",
        )
        self.assertEqual(kyc.address, "123 Main Street, Apartment 4B, New York, Ny 10001")

    def test_kyc_id_number_normalized_to_uppercase(self):
        """Test that ID number is normalized to uppercase"""
        user = self.create_user()
        kyc = KYC.objects.create(
            user=user,
            full_name="John Doe",
            phone="1234567890",
            address="123 main street",
            id_number="abc123xyz",
        )
        self.assertEqual(kyc.id_number, "ABC123XYZ")

    def test_kyc_id_number_mixed_case_normalized(self):
        """Test that mixed case ID number is normalized"""
        user = self.create_user()
        kyc = KYC.objects.create(
            user=user,
            full_name="John Doe",
            phone="1234567890",
            address="123 main street",
            id_number="AbC123XyZ",
        )
        self.assertEqual(kyc.id_number, "ABC123XYZ")

    def test_kyc_id_number_whitespace_trimmed(self):
        """Test that ID number whitespace is trimmed"""
        user = self.create_user()
        kyc = KYC.objects.create(
            user=user,
            full_name="John Doe",
            phone="1234567890",
            address="123 main street",
            id_number="  abc123  ",
        )
        self.assertEqual(kyc.id_number, "ABC123")

    # ========== Update Tests ==========

    def test_user_name_update_normalized(self):
        """Test that updating user names also normalizes them"""
        user = self.create_user()
        user.first_name = "jane"
        user.last_name = "smith"
        user.save()
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Jane")
        self.assertEqual(user.last_name, "Smith")

    def test_kyc_update_normalized(self):
        """Test that updating KYC fields also normalizes them"""
        user = self.create_user()
        kyc = KYC.objects.create(
            user=user,
            full_name="John Doe",
            phone="1234567890",
            address="123 main street",
            id_number="ABC123",
        )
        kyc.full_name = "jane smith"
        kyc.address = "456 oak avenue, apt 2b"
        kyc.id_number = "xyz789"
        kyc.save()
        kyc.refresh_from_db()
        self.assertEqual(kyc.full_name, "Jane Smith")
        self.assertEqual(kyc.address, "456 Oak Avenue, Apt 2B")
        self.assertEqual(kyc.id_number, "XYZ789")

    # ========== Edge Cases ==========

    def test_empty_first_name_handled(self):
        """Test that empty first_name doesn't cause errors"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", first_name="", password="testpass123"
        )
        self.assertEqual(user.first_name, "")

    def test_empty_last_name_handled(self):
        """Test that empty last_name doesn't cause errors"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", last_name="", password="testpass123"
        )
        self.assertEqual(user.last_name, "")

    def test_empty_kyc_fields_handled(self):
        """Test that empty KYC fields don't cause errors"""
        user = self.create_user()
        kyc = KYC.objects.create(
            user=user,
            full_name="",
            phone="",
            address="",
            id_number="",
        )
        self.assertEqual(kyc.full_name, "")
        self.assertEqual(kyc.address, "")
        self.assertEqual(kyc.id_number, "")

    def test_special_characters_in_names_preserved(self):
        """Test that special characters in names are preserved"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            first_name="o'brien",
            last_name="mc-donald",
            password="testpass123",
        )
        self.assertEqual(user.first_name, "O'Brien")
        self.assertEqual(user.last_name, "Mc-Donald")

    def test_hyphenated_names_normalized(self):
        """Test that hyphenated names are properly normalized"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            first_name="mary-jane",
            last_name="parker-watson",
            password="testpass123",
        )
        self.assertEqual(user.first_name, "Mary-Jane")
        self.assertEqual(user.last_name, "Parker-Watson")
