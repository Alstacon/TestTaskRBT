from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from lessons import models
from people import models as people_models
from people import serializers as people_serializers


class LessonSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField()
    teacher = serializers.SlugRelatedField(
        read_only=True,
        slug_field='full_name'
    )
    study_subject = serializers.SlugRelatedField(
        read_only=True,
        slug_field='title'
    )
    student_group = serializers.SlugRelatedField(
        read_only=True,
        slug_field='title'
    )
    missing_students = people_serializers.StudentSerializer(many=True)

    class Meta:
        model = models.Lesson
        fields = '__all__'


class LessonListSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField()
    teacher = serializers.SlugRelatedField(
        read_only=True,
        slug_field='full_name'
    )

    student_group = serializers.SlugRelatedField(
        read_only=True,
        slug_field='title'
    )
    missing_students = people_serializers.StudentSerializer(many=True)

    class Meta:
        model = models.Lesson
        exclude = ['id', 'study_subject']


class LessonCreateSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%d/%m/%Y %H:%M:%S'])

    class Meta:
        model = models.Lesson
        fields = '__all__'

    def validate(self, attrs: dict) -> dict:
        """Проверяет входные данные об отсутствующих студентах"""
        if 'missing_students' in attrs:
            if not attrs.get('status'):
                raise ValidationError({
                    'status': 'Нельзя добавить отсутствующих студентов до завершения занятия.'
                })
            if not attrs.get('student_group'):
                raise ValidationError({
                    'student_group': 'Введите группу обучаемых, чтобы добавить или изменить отсутствующих.'
                })
            else:
                students: list = attrs.pop('missing_students', [])
                attrs['missing_students'] = []
                for student in students:
                    if people_models.StudentGroup.objects.filter(Q(id=attrs['student_group'].id) & Q(students=student)):
                        attrs['missing_students'].append(student)

        return attrs


class LessonUpdateSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%d/%m/%Y %H:%M:%S'])

    class Meta:
        model = models.Lesson
        fields = '__all__'

    def update(self, instance: models.Lesson, validated_data: dict):
        if 'missing_students' in validated_data:
            if not instance.student_group and not validated_data.get('student_group'):
                raise ValidationError({
                    'student_group': 'Введите группу обучаемых, чтобы добавить или изменить отсутствующих.'
                })
            if not instance.status and not validated_data.get('status'):
                raise ValidationError({
                    'status': 'Нельзя добавить отсутствующих студентов до завершения занятия.'
                })
            else:
                students: list = validated_data.pop('missing_students', [])
                validated_data['missing_students'] = []
                student_group = validated_data.get('student_group') if validated_data.get(
                    'student_group') else instance.student_group

                for student in students:
                    if people_models.StudentGroup.objects.filter(
                            Q(id=student_group.id) & Q(students=student)):
                        validated_data['missing_students'].append(student)

        super().update(instance, validated_data)
        return instance


class StudySubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StudySubject
        fields = '__all__'


class StudySubjectDetailSerializer(serializers.ModelSerializer):
    lesson = LessonListSerializer(many=True)

    class Meta:
        model = models.StudySubject
        fields = '__all__'
