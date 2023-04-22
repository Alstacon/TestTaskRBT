from django.utils import timezone
import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from lessons.models import StudySubject, Lesson
from lessons.serializers import LessonSerializer, LessonUpdateSerializer
from people.models import Student, Teacher, StudentGroup


class TestLesson(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher_1 = Teacher.objects.create(full_name='Jake Epping', degree='Bachelor')

        cls.student_1 = Student.objects.create(full_name='Joe Doe')
        cls.student_2 = Student.objects.create(full_name='Sadie Dunhil')
        cls.student_3 = Student.objects.create(full_name='Lily Forest')

        cls.group_1 = StudentGroup.objects.create(title='Ivy')
        cls.group_1.students.set([cls.student_1, cls.student_2])

        cls.subject_1 = StudySubject.objects.create(title='Chemistry')
        cls.subject_2 = StudySubject.objects.create(title='History')

        cls.lesson_1 = Lesson.objects.create(
            date=timezone.now(),
            teacher=cls.teacher_1,
            study_subject=cls.subject_1,
            status=False,
        )
        cls.lesson_1.missing_students.set([1])

        cls.lesson_2 = Lesson.objects.create(
            date=timezone.now(),
            teacher=cls.teacher_1,
            study_subject=cls.subject_2,
            student_group=cls.group_1,
            status=False,
        )
        cls.lesson_2.missing_students.set([2])

    def test_create(self):
        self.assertEqual(2, Lesson.objects.all().count())
        url = reverse('lesson-list')
        data = json.dumps(
            {
                'date': '01/05/2023 10:00:00',
                'teacher': 1,
                'study_subject': 1,
                'student_group': 1,
                'status': False,
            })

        response = self.client.post(url, data=data, content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(3, Lesson.objects.all().count())

    def test_create_with_missing_stud_without_status(self):
        self.assertEqual(2, Lesson.objects.all().count())
        url = reverse('lesson-list')
        data = json.dumps(
            {
                'date': '01/05/2023 10:00:00',
                'teacher': 1,
                'study_subject': 1,
                'student_group': 1,
                'status': False,
                'missing_students': [1, 2, 3]
            })

        response = self.client.post(url, data=data, content_type='application/json')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(2, Lesson.objects.all().count())
        self.assertEqual(response.json()['status'],
                         ['Нельзя добавить отсутствующих студентов до завершения занятия.']
                         )

    def test_create_with_missing_stud_without_group(self):
        self.assertEqual(2, Lesson.objects.all().count())
        url = reverse('lesson-list')
        data = json.dumps(
            {
                'date': '01/05/2023 10:00:00',
                'teacher': 1,
                'study_subject': 1,
                'status': True,
                'missing_students': [1, 2, 3]
            })

        response = self.client.post(url, data=data, content_type='application/json')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(2, Lesson.objects.all().count())
        self.assertEqual(response.json()['student_group'],
                         ['Введите группу обучаемых, чтобы добавить или изменить отсутствующих.']
                         )

    def test_get_list(self):
        url = reverse('lesson-list')
        response = self.client.get(url)

        serializer_data = LessonSerializer([self.lesson_1, self.lesson_2], many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_retrieve(self):
        self.lesson_1.refresh_from_db()
        url = reverse('lesson-detail', args=[self.lesson_1.id])
        response = self.client.get(url)

        serializer_data = LessonSerializer(self.lesson_1).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_update(self):
        url = reverse('lesson-detail', args=[self.lesson_1.id])
        data = {
            'date': '01/05/2023 10:00:00',
            'teacher': 1,
            'study_subject': 2,
            'student_group': 1,
            'status': True,
            'missing_students': []
        }

        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')

        self.lesson_1.refresh_from_db()

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data['study_subject'], 2, self.lesson_1.study_subject.id)
        self.assertEqual(response.data['status'], True, self.lesson_1.status)

    def test_partial_update(self):
        self.assertEqual(1, self.lesson_1.study_subject.id)

        url = reverse('lesson-detail', args=[self.lesson_1.id])
        data = {
            'study_subject': 2,
        }

        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')

        self.lesson_1.refresh_from_db()

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data['study_subject'], 2, self.lesson_1.study_subject.id)

    def test_update_invalid(self):
        url = reverse('lesson-detail', args=[self.lesson_1.id])
        data = {
            'teacher': True
        }

        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')

        self.lesson_1.refresh_from_db()

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(self.teacher_1, self.lesson_1.teacher)

    def test_update_invalid_missing_students(self):
        url = reverse('lesson-detail', args=[self.lesson_1.id])
        data = {
            'date': '01/05/2023 10:00:00',
            'teacher': 1,
            'study_subject': 1,
            'student_group': 1,
            'status': True,
            'missing_students': [1, 2, 3]
        }

        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')

        self.lesson_1.refresh_from_db()
        ser_data = LessonUpdateSerializer(self.lesson_1).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual([1, 2], ser_data['missing_students'])

    def test_update_missing_students_before_end(self):
        url = reverse('lesson-detail', args=[self.lesson_1.id])
        data = {
            'student_group': 1,
            'missing_students': [1, 2, 3]
        }

        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')

        self.lesson_1.refresh_from_db()
        ser_data = LessonUpdateSerializer(self.lesson_1).data

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(response.json()['status'],
                         'Нельзя добавить отсутствующих студентов до завершения занятия.'
                         )

        self.assertEqual([1], ser_data['missing_students'])

    def test_update_missing_students_without_group(self):
        url = reverse('lesson-detail', args=[self.lesson_1.id])
        data = {
            'status': True,
            'missing_students': [1, 2, 3]
        }

        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')

        self.lesson_1.refresh_from_db()
        ser_data = LessonUpdateSerializer(self.lesson_1).data

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(response.json()['student_group'],
                         'Введите группу обучаемых, чтобы добавить или изменить отсутствующих.'
                         )

        self.assertEqual([1], ser_data['missing_students'])

    def test_delete(self):
        url = reverse('lesson-detail', args=[self.lesson_2.id])

        response = self.client.delete(url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(0, len(Lesson.objects.filter(id=self.lesson_2.id)))
