from rest_framework import viewsets

from people import models
from people import serializers


class StudentViewSet(viewsets.ModelViewSet):
    queryset = models.Student.objects.all()
    serializer_class = serializers.StudentSerializer


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = models.Teacher.objects.all()
    serializer_class = serializers.TeacherSerializer


class StudentGroupViewSet(viewsets.ModelViewSet):
    queryset = models.StudentGroup.objects.all()
    default_serializer_class = serializers.StudentGroupSerializer

    serializers = {
        'retrieve': serializers.StudentGroupDetailSerializer,
        'create': serializers.StudentGroupCreateSerializer,
        'update': serializers.StudentGroupUpdateSerializer,
        'partial_update': serializers.StudentGroupUpdateSerializer,

    }

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.default_serializer_class)
