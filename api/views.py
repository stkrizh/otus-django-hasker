from rest_framework.generics import ListCreateAPIView

from questions.models import Answer, Question

from .serializers import AnswerSerializer, QuestionSerializer


class QuestionsAPIView(ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class AnswersAPIView(ListCreateAPIView):
    serializer_class = AnswerSerializer

    def get_queryset(self):
        question_pk = self.kwargs.get("pk")
        queryset = Answer.objects.all()

        if question_pk is not None:
            queryset = queryset.filter(question=question_pk)

        return queryset
