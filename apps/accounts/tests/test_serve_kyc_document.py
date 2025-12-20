from unittest.mock import MagicMock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.accounts.models import KYC

from .base import BaseTestCase


class ServeKYCDocumentViewTests(BaseTestCase):
    def setUp(self):
        self.user = self.create_user()
        self.other_user = self.create_user(username="otheruser", email="other@example.com")
        self.kyc = KYC.objects.create(user=self.user)

    def test_serve_kyc_document_login_required(self):
        url = reverse("accounts:serve_kyc_document", args=[self.kyc.id, "front_image"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_serve_kyc_document_permission_denied(self):
        self.client.force_login(self.other_user)
        url = reverse("accounts:serve_kyc_document", args=[self.kyc.id, "front_image"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_serve_kyc_document_superuser_access(self):
        superuser = self.user_model.objects.create_superuser(
            username="admin", email="admin@example.com", password=self.user_password
        )
        self.client.force_login(superuser)
        url = reverse("accounts:serve_kyc_document", args=[self.kyc.id, "front_image"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_serve_kyc_document_invalid_field(self):
        self.client.force_login(self.user)
        url = reverse("accounts:serve_kyc_document", args=[self.kyc.id, "invalid_field"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_serve_kyc_document_file_not_found(self):
        self.client.force_login(self.user)
        url = reverse("accounts:serve_kyc_document", args=[self.kyc.id, "front_image"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    @patch("django.core.files.storage.FileSystemStorage.open")
    def test_serve_kyc_document_success(self, mock_open):
        self.client.force_login(self.user)
        self.kyc.front_image = SimpleUploadedFile("test.jpg", b"file_content")
        self.kyc.save()

        mock_file = MagicMock()
        mock_file.read.return_value = b"file_content"
        mock_open.return_value = mock_file

        url = reverse("accounts:serve_kyc_document", args=[self.kyc.id, "front_image"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/jpeg")

    @patch("django.core.files.storage.FileSystemStorage.open")
    def test_serve_kyc_document_file_not_found_on_disk(self, mock_open):
        self.client.force_login(self.user)
        self.kyc.front_image = SimpleUploadedFile("test.jpg", b"file_content")
        self.kyc.save()

        mock_open.side_effect = FileNotFoundError()

        url = reverse("accounts:serve_kyc_document", args=[self.kyc.id, "front_image"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
