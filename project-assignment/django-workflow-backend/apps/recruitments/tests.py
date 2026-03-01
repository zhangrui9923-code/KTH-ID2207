from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Recruitment

User = get_user_model()

class RecruitmentFlowTests(APITestCase):
    def setUp(self):
        self.sm = User.objects.create_user(username="sm", password="x", role="sm")
        self.hrm = User.objects.create_user(username="hrm", password="x", role="hrm")

    def auth(self, user):
        self.client.force_authenticate(user=user)

    def test_happy_path(self):
        self.auth(self.sm)
        r = self.client.post("/api/recruitments/", {
            "position_title": "Backend Engineer",
            "description": "Scale services",
            "department": "IT",
            "number_of_positions": 2
        }, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        rid = r.data["id"]

        s = self.client.post(f"/api/recruitments/{rid}/submit/")
        self.assertEqual(s.status_code, status.HTTP_200_OK)
        self.assertEqual(s.data["status"], Recruitment.Status.SUBMITTED)

        self.auth(self.hrm)
        a = self.client.post(f"/api/recruitments/{rid}/accept/")
        self.assertEqual(a.status_code, status.HTTP_200_OK)
        self.assertEqual(a.data["status"], Recruitment.Status.IN_PROGRESS)

        i1 = self.client.post(f"/api/recruitments/{rid}/add_interview/")
        self.assertEqual(i1.status_code, status.HTTP_200_OK)

        h = self.client.post(f"/api/recruitments/{rid}/add_hires/", {"count": 2}, format="json")
        self.assertEqual(h.status_code, status.HTTP_200_OK)
        self.assertEqual(h.data["positions_filled"], 2)

        c = self.client.post(f"/api/recruitments/{rid}/complete/")
        self.assertEqual(c.status_code, status.HTTP_200_OK)
        self.assertEqual(c.data["status"], Recruitment.Status.COMPLETED)

