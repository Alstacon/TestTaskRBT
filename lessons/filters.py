from django_filters import rest_framework as filters

from lessons.models import Lesson


class LessonFilter(filters.FilterSet):
    class Meta:
        model = Lesson
        fields = ('study_subject', 'teacher', 'student_group', 'status')
