from django.urls import include, path

from . import views

urlpatterns = [
    path("questions", views.QuestionsAPIView.as_view(), name="api_questions"),
    path(
        "questions/<int:pk>/answers",
        views.AnswersAPIView.as_view(),
        name="api_answers",
    ),
]
