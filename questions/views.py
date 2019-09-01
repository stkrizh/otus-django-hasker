from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .forms import AskForm
from .models import Question


class Questions(ListView):
    model = Question
    paginate_by = 10
    ordering = "-posted"
    template_name = "questions.html"


class QuestionsPopular(Questions):
    ordering = "title"


class Ask(LoginRequiredMixin, CreateView):
    form_class = AskForm
    login_url = reverse_lazy("login")
    model = Question
    template_name = "ask.html"
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        """If the form is valid, save the question and its tags.
        """
        question = form.save(commit=False)
        question.author = self.request.user
        question.save()

        raw_tags = form.cleaned_data["tags"]
        question.add_tags(raw_tags, self.request.user)

        messages.success(
            self.request, "Your question has been added successfully!"
        )
        return redirect(self.success_url)
