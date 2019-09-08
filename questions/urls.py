"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from . import views


urlpatterns = [
    path("", views.Questions.as_view(), name="index"),
    path(
        "answer/mark/<int:answer_id>",
        views.AnswerMark.as_view(),
        name="answer_mark",
    ),
    path("ask", views.Ask.as_view(), name="ask"),
    path("latest", views.Questions.as_view(), name="latest"),
    path("popular", views.QuestionsPopular.as_view(), name="popular"),
    path("search", views.QuestionsSearch.as_view(), name="search"),
    path("tag/<tag>", views.QuestionsTag.as_view(), name="tag"),
    path(
        "questions/<int:question_id>",
        views.QuestionDetail.as_view(),
        name="question_detail",
    ),
    path("vote/question", views.QuestionVote.as_view(), name="vote_question"),
    path("vote/answer", views.AnswerVote.as_view(), name="vote_answer"),
]
