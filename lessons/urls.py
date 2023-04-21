from rest_framework.routers import SimpleRouter
from django.urls import include, path


from lessons import views

router = SimpleRouter()

router.register('subject', views.StudySubjectViewSet, basename='subject')
router.register('lesson', views.LessonViewSet, basename='lesson')
# router.register('group', views.StudentGroupViewSet, basename='group')

urlpatterns = [
    path('', include(router.urls)),
]
