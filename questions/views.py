from django.views.generic import ListView

from questions.models import Question


class Index(ListView):
    model = Question
    template_name = "questions.html"
