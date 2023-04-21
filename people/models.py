from django.db import models


class Person(models.Model):
    class Meta:
        abstract = True

    full_name = models.CharField(max_length=255, verbose_name='ФИО')


class Student(Person):
    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'

    def __str__(self):
        return self.full_name


class Teacher(Person):
    degree = models.CharField(max_length=255, verbose_name='Ученая степень')

    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'

    def __str__(self):
        return self.full_name


class StudentGroup(models.Model):
    title = models.CharField(max_length=255, verbose_name='Наименование')
    students = models.ManyToManyField(Student, verbose_name='Идентификаторы студентов')

    class Meta:
        verbose_name = 'Группа обучаемых'
        verbose_name_plural = 'Группы обучаемых'

    def __str__(self):
        return self.title
