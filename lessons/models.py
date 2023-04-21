from django.db import models

from people.models import Teacher, StudentGroup, Student


class StudySubject(models.Model):
    title = models.CharField(max_length=255, verbose_name='Наименование')

    class Meta:
        verbose_name = 'Предмет обучения'
        verbose_name_plural = 'Предметы обучения'

    def __str__(self):
        return self.title


class Lesson(models.Model):
    study_subject = models.ForeignKey(StudySubject, on_delete=models.CASCADE, verbose_name='Предмет обучения')
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT, verbose_name='Преподаватель')
    student_group = models.ForeignKey(StudentGroup, on_delete=models.PROTECT, verbose_name='Группы обучаемых')
    date = models.DateTimeField(verbose_name='Дата проведения')
    status = models.BooleanField(default=False, verbose_name='Состояние занятия')
    missing_students = models.ManyToManyField(Student, verbose_name='Отсутствующие студенты')

    class Meta:
        verbose_name = 'Занятие'
        verbose_name_plural = 'Занятия'

    def __str__(self):
        return self.study_subject
