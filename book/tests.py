from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class EmployeeViewTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="Admin123456",
        )
        self.staff_user = User.objects.create_user(
            username="staff_user",
            email="staff@example.com",
            password="Staff123456",
            is_staff=True,
        )
        self.member_user = User.objects.create_user(
            username="member_user",
            email="member@example.com",
            password="Member123456",
        )
        self.client.force_login(self.admin)

    def test_employee_list_excludes_registered_non_staff_users(self):
        response = self.client.get(reverse("employees_list"))

        self.assertEqual(response.status_code, 200)
        employees = list(response.context["employees"])
        self.assertIn(self.staff_user, employees)
        self.assertNotIn(self.member_user, employees)

    def test_employee_detail_rejects_registered_non_staff_users(self):
        response = self.client.get(
            reverse("employees_detail", kwargs={"pk": self.member_user.pk})
        )

        self.assertEqual(response.status_code, 404)
