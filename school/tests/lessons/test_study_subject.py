import json
from django.utils import timezone

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from lessons.models import StudySubject, Lesson
from lessons.serializers import StudySubjectSerializer, StudySubjectDetailSerializer
from people.models import Student, Teacher, StudentGroup


class TestStudySubject(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher_1 = Teacher.objects.create(full_name='Jake Epping', degree='Bachelor')
        cls.student_1 = Student.objects.create(full_name='Joe Doe')
        cls.student_2 = Student.objects.create(full_name='Sadie Dunhil')

        cls.group_1 = StudentGroup.objects.create(title='Ivy')
        cls.group_1.students.set([cls.student_1, cls.student_2])

        cls.subject_1 = StudySubject.objects.create(title='Chemistry')
        cls.subject_2 = StudySubject.objects.create(title='History')

        cls.lesson_1 = Lesson.objects.create(
            date=timezone.now(),
            teacher=cls.teacher_1,
            study_subject=cls.subject_1,
            student_group=cls.group_1,
            status=False,
        )

    def test_create(self):
        self.assertEqual(2, StudySubject.objects.all().count())

        url = reverse('subject-list')
        data = {
            'title': 'Math'
        }

        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(3, StudySubject.objects.all().count())

        subject_3 = StudySubject.objects.last()

        self.assertEqual(subject_3.title, 'Math')

    def test_get_list(self):
        url = reverse('subject-list')
        response = self.client.get(url)

        serializer_data = StudySubjectSerializer([self.subject_1, self.subject_2], many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_retrieve(self):
        self.subject_1.refresh_from_db()
        url = reverse('subject-detail', args=[self.subject_1.id])
        response = self.client.get(url)

        serializer_data = StudySubjectDetailSerializer(self.subject_1).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_update(self):
        self.subject_1.refresh_from_db()
        url = reverse('subject-detail', args=[self.subject_1.id])
        data = {
            'title': 'PE'
        }

        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')

        self.subject_1.refresh_from_db()

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data['title'], 'PE', self.subject_1.title)

    def test_update_invalid(self):
        self.subject_2.refresh_from_db()
        url = reverse('subject-detail', args=[self.subject_2.id])
        data = {
            'title': True
        }

        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')

        self.subject_2.refresh_from_db()

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual('History', self.subject_2.title)

    def test_delete(self):
        sub_id = self.subject_1.id

        url = reverse('subject-detail', args=[sub_id])
        self.assertTrue(Lesson.objects.get(study_subject=sub_id))

        response = self.client.delete(url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(0, len(StudySubject.objects.filter(id=self.subject_1.id)))
        self.assertFalse(Lesson.objects.filter(study_subject=sub_id))
