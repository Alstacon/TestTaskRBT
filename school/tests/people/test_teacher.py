from datetime import datetime
import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from lessons.models import Lesson, StudySubject
from people.models import Teacher, StudentGroup, Student
from people.serializers import TeacherSerializer


class TestTeacher(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student_1 = Student.objects.create(full_name='Joe Doe')
        cls.student_2 = Student.objects.create(full_name='Sadie Dunhil')
        cls.teacher_1 = Teacher.objects.create(full_name='Jake Epping', degree='Bachelor')
        cls.teacher_2 = Teacher.objects.create(full_name='Sadie Dunhil', degree='Master')

        cls.subject_1 = StudySubject.objects.create(title='Chemistry')

        cls.group_1 = StudentGroup.objects.create(title='Ivy')
        cls.group_1.students.set([cls.student_1, cls.student_2])

        cls.lesson_1 = Lesson.objects.create(
            date=datetime.today(),
            teacher=cls.teacher_1,
            study_subject=cls.subject_1,
            student_group=cls.group_1,
            status=False,
        )

    def test_create(self):
        self.assertEqual(2, Teacher.objects.all().count())

        url = reverse('teacher-list')
        data = {
            'full_name': 'George Mohrenschildt',
            'degree': 'Doctor'
        }

        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(3, Teacher.objects.all().count())

        teacher_3 = Teacher.objects.last()

        self.assertEqual(teacher_3.full_name, 'George Mohrenschildt')
        self.assertEqual(teacher_3.degree, 'Doctor')

    def test_get_list(self):
        url = reverse('teacher-list')
        response = self.client.get(url)

        serializer_data = TeacherSerializer([self.teacher_1, self.teacher_2], many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_retrieve(self):
        self.teacher_1.refresh_from_db()
        url = reverse('teacher-detail', args=[self.teacher_1.id])
        response = self.client.get(url)

        serializer_data = TeacherSerializer(self.teacher_1).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_partial_update(self):
        url = reverse('teacher-detail', args=[self.teacher_1.id])
        data = {
            'degree': 'Master'
        }

        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')

        self.teacher_1.refresh_from_db()

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data['degree'], 'Master', self.teacher_1.degree)

    def test_update(self):
        url = reverse('teacher-detail', args=[self.teacher_1.id])
        data = {
            'full_name': 'James Hosty',
            'degree': 'Master'
        }

        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')

        self.teacher_1.refresh_from_db()

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data['degree'], 'Master', self.teacher_1.degree)
        self.assertEqual(response.data['full_name'], 'James Hosty', self.teacher_1.full_name)

    def test_update_invalid(self):
        url = reverse('teacher-detail', args=[self.teacher_1.id])
        data = {
            'degree': True
        }

        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')

        self.teacher_1.refresh_from_db()

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual('Bachelor', self.teacher_1.degree)

    def test_delete(self):
        teacher_id = self.teacher_1.id
        url = reverse('teacher-detail', args=[teacher_id])

        lessons = Lesson.objects.filter(study_subject=teacher_id)

        response = self.client.delete(url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(0, len(Teacher.objects.filter(id=self.teacher_1.id)))
        for item in lessons:
            self.assertFalse(item.teacher, None)
