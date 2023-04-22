import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from people.models import Student
from people.serializers import StudentSerializer


class TestStudent(TestCase):
    def setUp(self):
        self.student_1 = Student.objects.create(full_name='Jake Epping')
        self.student_2 = Student.objects.create(full_name='Sadie Dunhil')

    def test_create(self):
        self.assertEqual(2, Student.objects.all().count())

        url = reverse('student-list')
        data = {
            'full_name': 'George Mohrenschildt'
        }

        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(3, Student.objects.all().count())

        student_3 = Student.objects.last()

        self.assertEqual(student_3.full_name, 'George Mohrenschildt')

    def test_get_list(self):
        url = reverse('student-list')
        response = self.client.get(url)

        serializer_data = StudentSerializer([self.student_1, self.student_2], many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_retrieve(self):
        url = reverse('student-detail', args=[self.student_1.id])
        response = self.client.get(url)

        serializer_data = StudentSerializer(self.student_1).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_update(self):
        url = reverse('student-detail', args=[self.student_1.id])
        data = {
            'full_name': 'Deacon Simmons'
        }

        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')

        self.student_1.refresh_from_db()

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data['full_name'], 'Deacon Simmons', self.student_1.full_name)

    def test_update_invalid(self):
        url = reverse('student-detail', args=[self.student_1.id])
        data = {
            'full_name': True
        }

        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')

        self.student_1.refresh_from_db()

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual('Jake Epping', self.student_1.full_name)

    def test_delete(self):
        url = reverse('student-detail', args=[self.student_1.id])

        response = self.client.delete(url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(0, len(Student.objects.filter(id=self.student_1.id)))
