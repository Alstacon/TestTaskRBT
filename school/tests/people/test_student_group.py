import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from lessons.models import Lesson
from people.models import StudentGroup, Student
from people.serializers import StudentGroupSerializer, StudentGroupCreateSerializer, \
    StudentGroupDetailSerializer


class TestTeacher(TestCase):
    def setUp(self):
        self.student_1 = Student.objects.create(full_name='Jake Epping')
        self.student_2 = Student.objects.create(full_name='Sadie Dunhil')
        self.student_3 = Student.objects.create(full_name='Joe Doe')

        self.group_1 = StudentGroup.objects.create(title='Ivy')
        self.group_1.students.set([self.student_1, self.student_2])
        self.group_2 = StudentGroup.objects.create(title='Oak')
        self.group_2.students.set([self.student_3])

    def test_create_with_existing_student(self):
        self.assertEqual(2, StudentGroup.objects.all().count())

        url = reverse('group-list')
        data = {
            'title': 'Aspen',
            'students': [
                {'full_name': 'Sadie Dunhil'},
                {'full_name': 'Jake Epping'}
            ]
        }

        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(3, StudentGroup.objects.all().count())

        group_3 = StudentGroup.objects.last()
        serialized_data = StudentGroupCreateSerializer(group_3).data

        self.assertEqual(response.data, serialized_data)

    def test_create_with_new_student(self):
        self.assertEqual(2, StudentGroup.objects.all().count())

        url = reverse('group-list')
        data = {
            'title': 'Aspen',
            'students': [
                {'full_name': 'Ariel Moonlight'}]
        }

        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(3, StudentGroup.objects.all().count())

        group_3 = StudentGroup.objects.last()
        serialized_data = StudentGroupCreateSerializer(group_3).data

        self.assertEqual(response.data, serialized_data)

        new_student = Student.objects.last()
        self.assertEqual(new_student.full_name, 'Ariel Moonlight')

    def test_get_list(self):
        url = reverse('group-list')
        response = self.client.get(url)

        serializer_data = StudentGroupSerializer([self.group_1, self.group_2], many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_retrieve(self):
        url = reverse('group-detail', args=[self.group_1.id])
        response = self.client.get(url)

        serializer_data = StudentGroupDetailSerializer(self.group_1).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_partial_update(self):
        url = reverse('group-detail', args=[self.group_1.id])
        data = {
            'title': 'Linden'
        }

        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')

        self.group_1.refresh_from_db()

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data['title'], 'Linden', self.group_1.title)

    def test_update(self):
        url = reverse('group-detail', args=[self.group_1.id])
        data = {
            'title': 'Linden',
            'students': [
                {'full_name': 'Joe Doe'}]
        }

        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')

        self.group_1.refresh_from_db()

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data['title'], 'Linden', self.group_1.title)
        self.assertEqual(len(response.data['students']), 1)
        self.assertEqual(response.data['students'][0]['full_name'], 'Joe Doe')

    def test_update_invalid(self):
        url = reverse('group-detail', args=[self.group_1.id])

        data = {
            'students': 1
        }

        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')

        self.group_1.refresh_from_db()
        serialized_data = StudentGroupDetailSerializer(self.group_1).data

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(len(serialized_data['students']), 2)

    def test_delete(self):
        group_id = self.group_1.id
        url = reverse('group-detail', args=[group_id])

        lessons = Lesson.objects.filter(student_group=group_id)
        response = self.client.delete(url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(0, len(StudentGroup.objects.filter(id=self.group_1.id)))
        for item in lessons:
            self.assertEqual(item.student_group, None)
