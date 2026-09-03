import unittest
from app import app, db, Students

class StudentAppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_1_show_all_screen(self):
        """Test GET / screen displays phone column, User ID footnote, and existing students."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("All Students", html)
        self.assertIn("6580109", html)
        self.assertIn("<th>Phone</th>", html)
        self.assertIn("Hassan Ali", html)
        self.assertIn("Yuusuf Garaad Mire", html)
        self.assertIn('href="/new"', html)

    def test_2_new_student_get_screen(self):
        """Test GET /new screen displays the form with phone number input and User ID footnote."""
        response = self.client.get('/new')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Add New Student", html)
        self.assertIn("6580109", html)
        self.assertIn('name="phone"', html)
        self.assertIn('Phone Number:', html)

    def test_3_new_student_post_validation_error(self):
        """Test POST /new with missing required fields triggers flash error."""
        response = self.client.post('/new', data={
            'name': '',
            'city': 'Miami',
            'addr': '',
            'pin': '',
            'phone': ''
        })
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Please enter all the fields", html)

    def test_4_new_student_post_success(self):
        """Test POST /new successfully adds a student with phone number and redirects."""
        test_student_name = "Automated Test Student"
        response = self.client.post('/new', data={
            'name': test_student_name,
            'city': 'Tampa',
            'addr': '789 Bay Shore Dr',
            'pin': '33601',
            'phone': '813-555-0144'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Record was successfully added", html)
        self.assertIn(test_student_name, html)
        self.assertIn("813-555-0144", html)

        # Verify in database and clean up test record
        with app.app_context():
            student = Students.query.filter_by(name=test_student_name).first()
            self.assertIsNotNone(student)
            self.assertEqual(student.phone, '813-555-0144')
            db.session.delete(student)
            db.session.commit()

if __name__ == '__main__':
    unittest.main()
