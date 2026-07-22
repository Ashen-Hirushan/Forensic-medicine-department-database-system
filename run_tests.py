import os
import unittest
from app import create_app
from app.services.db import execute_query

class SystemIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize the app with test configuration if necessary
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.app.config['WTF_CSRF_ENABLED'] = False
        cls.client = cls.app.test_client()

    def login(self, username, password):
        return self.client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def test_1_authentication(self):
        """Test login with valid credentials"""
        response = self.login('admin_user', 'securepass123')
        self.assertIn(b'Dashboard', response.data)
        self.logout()

    def test_2_rbac_security(self):
        """Verify role-based access control"""
        # Login as Doctor
        self.login('dr_chathula', 'securepass123')
        
        # Doctor should be able to access Clinical Cases
        clinical_response = self.client.get('/clinical/')
        self.assertEqual(clinical_response.status_code, 200)
        self.assertIn(b'Clinical Examinations', clinical_response.data)
        
        # Doctor should NOT be able to access Court Dispatches
        court_response = self.client.get('/court/dispatch')
        self.assertEqual(court_response.status_code, 403) # Forbidden
        
        self.logout()

    def test_3_clinical_case_creation(self):
        """Test inserting a new clinical case"""
        self.login('dr_chathula', 'securepass123')
        
        response = self.client.post('/clinical/new', data=dict(
            nic='TEST-NIC-001',
            name='Test Patient Integration',
            age='30',
            gender='Male',
            address='123 Test Street',
            contact='0770000000',
            facility_id='1',
            station_id='1',
            assigned_doctor_id='2',
            reference_no='TEST-REF-001',
            incident_date='2024-06-01T10:00',
            admission_date='2024-06-01T12:00',
            hospital_bht_no='BHT-TEST'
        ), follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Clinical case registered successfully', response.data)
        self.logout()

    def test_4_dashboard_stats(self):
        """Verify dashboard loads properly and doesn't crash on stats"""
        self.login('admin_user', 'securepass123')
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        # Should render the charts block
        self.assertIn(b'Clinical Cases', response.data)
        self.assertIn(b'Autopsies (This Month)', response.data)
        self.logout()
        
    def test_5_evidence_transfer(self):
        """Test recording evidence transfer"""
        # Login as Lab Staff
        self.login('lab_kamal', 'securepass123')
        response = self.client.post('/evidence/transfer', data=dict(
            evidence_id='1',
            to_user_id='5',
            location='Lab Test Transfer Area'
        ), follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Evidence transferred successfully!', response.data)
        self.logout()

if __name__ == '__main__':
    unittest.main(verbosity=2)
