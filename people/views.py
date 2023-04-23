from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from people import models
from people import serializers


class StudentViewSet(viewsets.ModelViewSet):
    queryset = models.Student.objects.all()
    serializer_class = serializers.StudentSerializer
    ordering = ['full_name']


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = models.Teacher.objects.all()
    serializer_class = serializers.TeacherSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ['full_name']


class StudentGroupViewSet(viewsets.ModelViewSet):
    queryset = models.StudentGroup.objects.prefetch_related('students')
    default_serializer_class = serializers.StudentGroupSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ['id']

    serializers = {
        'retrieve': serializers.StudentGroupDetailSerializer,
        'create': serializers.StudentGroupCreateSerializer,
        'update': serializers.StudentGroupUpdateSerializer,
        'partial_update': serializers.StudentGroupUpdateSerializer,

    }

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.default_serializer_class)
