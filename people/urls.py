from rest_framework.routers import SimpleRouter
from django.urls import include, path


from people import views

router = SimpleRouter()

router.register('student', views.StudentViewSet, basename='student')
router.register('teacher', views.TeacherViewSet, basename='teacher')
router.register('group', views.StudentGroupViewSet, basename='group')

urlpatterns = [
    path('', include(router.urls)),
]
