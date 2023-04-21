from django.db.models import Q
from rest_framework import serializers

from lessons import models
from people import models as people_models


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

    class Meta:
        model = models.Lesson
        fields = '__all__'


class LessonListSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField()

    class Meta:
        model = models.Lesson
        exclude = ['id', 'study_subject']


class LessonCreateUpdateSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%d/%m/%Y %H:%M:%S'])

    class Meta:
        model = models.Lesson
        fields = '__all__'

    def validate(self, attrs: dict) -> dict:
        students: list = attrs.pop('missing_students', [])
        attrs['missing_students'] = []
        for student in students:
            if people_models.StudentGroup.objects.filter(Q(id=attrs['student_group'].id) & Q(students=student)):
                attrs['missing_students'].append(student)
        return attrs


class StudySubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StudySubject
        fields = '__all__'
        read_only_fields = ['id']


class StudySubjectDetailSerializer(serializers.ModelSerializer):
    lesson = LessonListSerializer(many=True)

    class Meta:
        model = models.StudySubject
        fields = '__all__'
