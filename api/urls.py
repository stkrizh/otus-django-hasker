from django.urls import path

from rest_framework.authtoken.views import obtain_auth_token

from . import views


urlpatterns = [
    path("token", obtain_auth_token, name="api_obtain_token"),
    path("questions", views.QuestionsAPIView.as_view(), name="api_questions"),
    path(
        "questions/<int:pk>/answers",
        views.AnswersAPIView.as_view(),
        name="api_answers",
    ),
]
