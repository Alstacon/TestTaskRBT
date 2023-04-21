from django.contrib import admin

from people.models import Student, Teacher, StudentGroup

admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(StudentGroup)
