from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .forms import AnswerForm, AskForm
from .models import Answer, Question


class QuestionDetail(ListView):
    form = None
    model = Answer
    ordering = "posted"
    paginate_by = 3
    template_name = "answers.html"

    def dispatch(self, *args, **kwargs):
        self.question = get_object_or_404(
            Question, pk=self.kwargs["question_id"]
        )
        return super().dispatch(*args, **kwargs)

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form.
        """
        self.form = form
        messages.error(
            self.request,
            "Your answer couldn't be submitted. Please see the error below.",
        )
        return super().get(self.request)

    def form_valid(self, form):
        """If the form is valid, save the answer.
        """
        answer = form.save(commit=False)
        answer.author = self.request.user
        answer.question = self.question
        answer.save()

        messages.success(self.request, "Thank you for your answer!")
        return redirect(self.request.build_absolute_uri())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["question"] = self.question

        if self.form is not None:
            context["form"] = self.form

        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(question=self.question)

    def post(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseForbidden()

        form = AnswerForm(data=self.request.POST)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


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
