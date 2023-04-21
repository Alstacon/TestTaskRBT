from rest_framework import viewsets

from lessons import models
from lessons import serializers
from django_filters.rest_framework import DjangoFilterBackend

from lessons.filters import LessonFilter


class StudySubjectViewSet(viewsets.ModelViewSet):
    default_queryset = models.StudySubject.objects.all()
    default_serializer_class = serializers.StudySubjectSerializer

    querysets = {
        'retrieve': models.StudySubject.objects.select_related('lesson')
    }
    serializers = {
        'retrieve': serializers.StudySubjectDetailSerializer
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.default_serializer_class)

    def get_queryset(self):
        return self.querysets.get(self.action, self.default_queryset)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = models.Lesson.objects.select_related('study_subject', 'teacher',
                                                    'student_group').prefetch_related('missing_students')
    default_serializer_class = serializers.LessonSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = LessonFilter

    serializers = {
        'retrieve': serializers.LessonSerializer,
        'create': serializers.LessonCreateUpdateSerializer,
        'update': serializers.LessonCreateUpdateSerializer,
        'partial_update': serializers.LessonCreateUpdateSerializer,
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.default_serializer_class)
