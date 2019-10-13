from django.urls import path

from rest_framework.authtoken.views import obtain_auth_token

from . import views


urlpatterns = [
    path("token", obtain_auth_token, name="api_obtain_token"),
    path("questions", views.QuestionsAPIView.as_view(), name="api_questions"),
    path(
        "questions/<int:pk>",
        views.QuestionDetailsAPIView.as_view(),
        name="api_question_details",
    ),
    path(
        "questions/<int:pk>/answers",
        views.AnswersAPIView.as_view(),
        name="api_answers",
    ),
    path(
        "questions/<int:pk>/votes",
        views.QuestionVotesAPIView.as_view(),
        name="api_question_votes",
    ),
    path(
        "questions/<int:question_pk>/votes/<int:pk>",
        views.QuestionVoteDetailsAPIView.as_view(),
        name="api_question_vote_details",
    ),
    path(
        "answers/<int:pk>",
        views.AnswerDetailsAPIView.as_view(),
        name="api_answer_details",
    ),
    path(
        "answers/<int:pk>/votes",
        views.AnswerVotesAPIView.as_view(),
        name="api_answer_votes",
    ),
    path(
        "answers/<int:answer_pk>/votes/<int:pk>",
        views.AnswerVoteDetailsAPIView.as_view(),
        name="api_answer_vote_details",
    ),
]
