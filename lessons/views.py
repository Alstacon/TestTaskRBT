from rest_framework import viewsets

from lessons import models
from lessons import serializers
from django_filters.rest_framework import DjangoFilterBackend

from lessons.filters import LessonFilter


class StudySubjectViewSet(viewsets.ModelViewSet):
    queryset = models.StudySubject.objects.prefetch_related('lesson')
    default_serializer_class = serializers.StudySubjectSerializer

    serializers = {
        'retrieve': serializers.StudySubjectDetailSerializer
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.default_serializer_class)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = models.Lesson.objects.select_related('study_subject', 'teacher',
                                                    'student_group').prefetch_related('missing_students')
    default_serializer_class = serializers.LessonSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = LessonFilter

    serializers = {
        'create': serializers.LessonCreateSerializer,
        'update': serializers.LessonUpdateSerializer,
        'partial_update': serializers.LessonUpdateSerializer,
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.default_serializer_class)
