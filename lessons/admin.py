from django.contrib import admin

from lessons.models import Lesson, StudySubject

admin.site.register(StudySubject)
admin.site.register(Lesson)
