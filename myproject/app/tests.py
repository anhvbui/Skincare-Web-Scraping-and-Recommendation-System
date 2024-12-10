from django.test import TestCase

# Create your tests here.

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from .views import assign_att_score

class AssignAttScoreTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='anhb', password='rileynofleas')
        self.factory = RequestFactory()

    def test_assign_att_score(self):
        mock_request = self.factory.get('/')
        mock_request.user = self.user

        mock_data = [
            {
                "name": "skin_concerns",
                "value": "Acne"},
            {
                "name": "skin_concerns",
                "value": "Oily"},
            {
                "name": "skin_concerns",
                "value": "Soothing"},
            {
                "name": "skin_concerns",
                "value": "Dullness"},
            {
                "name": "skin_concerns",
                "value": "Stress"},
            {
                "name": "skin_type",
                "value": "Normal"},
            {
                "name": "age",
                "value": "25-49"},
            {
                "name": "verify_skin_type",
                "value": "Dry" },
            {
                "name": "sensitivity_adj",
                "value": "0.3"},
            {
                "name": "routine_steps",
                "value": "6"},
            {
                "name": "sun_care_adj",
                "value": "0.3"},
            {
                "name": "makeup_YN",
                "value": "Y"}
            ]

        result = assign_att_score(mock_data, mock_request)
        self.assertEqual(result['user_id'], self.user.id)
        self.assertEqual(result['routine_steps'], 6)
        self.assertEqual(result['Soothing'], 0.5)
        self.assertEqual(result['Sun Care'], 0.3)
        self.assertEqual(result['Acne'], 0.2)  