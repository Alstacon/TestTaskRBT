from django.db import transaction
from rest_framework import serializers

from people import models


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Student
        fields = '__all__'
        read_only_fields = ['id']


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Teacher
        fields = '__all__'
        read_only_fields = ['id']


class StudentGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StudentGroup
        fields = '__all__'


class StudentGroupDetailSerializer(serializers.ModelSerializer):
    students = StudentSerializer(many=True)

    class Meta:
        model = models.StudentGroup
        fields = '__all__'


class StudentGroupCreateSerializer(serializers.ModelSerializer):
    students = StudentSerializer(many=True, required=False)

    class Meta:
        model = models.StudentGroup
        fields = '__all__'
        read_only_fields = ['id']

    def create(self, validated_data: dict) -> models.StudentGroup:
        students: list = validated_data.pop('students', [])
        group: models.StudentGroup = models.StudentGroup.objects.create(**validated_data)

        for item in students:
            student, _ = models.Student.objects.get_or_create(
                full_name=item['full_name'],
            )
            group.students.add(student)

        group.save()
        return group


class StudentGroupUpdateSerializer(serializers.ModelSerializer):
    students = StudentSerializer(many=True, required=False)

    class Meta:
        model = models.StudentGroup
        fields = '__all__'
        read_only_fields = ['id']

    def update(self, instance: models.StudentGroup, validated_data: dict) -> models.StudentGroup:
        with transaction.atomic():
            if 'students' in validated_data:
                instance.students.clear()
                students: list = validated_data.pop('students', [])
                for item in students:
                    student, _ = models.Student.objects.get_or_create(
                        full_name=item['full_name'],
                    )
                    instance.students.add(student)
            super().update(instance, validated_data)
        return instance
