from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from questions.models import Answer, Question

from .serializers import AnswerSerializer, QuestionSerializer


class QuestionsAPIView(ListCreateAPIView):
    VALID_SORTS = {
        "latest": "-posted",
        "popular": "-rating",
        "trending": "-number_of_votes",
    }

    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = QuestionSerializer

    def get(self, request, *args, **kwargs):
        self.sort = request.query_params.get("sort", "latest")

        if self.sort not in self.VALID_SORTS:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return super().get(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = Question.objects.all()
        queryset = queryset.select_related("author")
        queryset = queryset.prefetch_related("tags")
        queryset = queryset.order_by(self.VALID_SORTS[self.sort])

        return queryset


class QuestionDetailsAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = QuestionSerializer

    def get_queryset(self):
        queryset = Question.objects.all()
        queryset = queryset.select_related("author")
        queryset = queryset.prefetch_related("tags")

        return queryset


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
        queryset = queryset.order_by("-is_accepted", "-rating", "-posted")

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, question=self.question)
