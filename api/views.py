from django.shortcuts import get_object_or_404

from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from questions.models import Answer, Question

from .serializers import AnswerSerializer, QuestionSerializer


class QuestionsAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class AnswersAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = AnswerSerializer

    def initial(self, request, *args, **kwargs):
        """
        Runs anything that needs to occur prior to calling the method handler.
        """
        super().initial(request, *args, **kwargs)
        self.question = get_object_or_404(Question, pk=self.kwargs.get("pk"))

    def get_queryset(self):
        queryset = Answer.objects.all()
        queryset = queryset.filter(question=self.question)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, question=self.question)
