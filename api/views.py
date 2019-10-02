from django.shortcuts import get_object_or_404

from rest_framework import filters
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from questions.models import Answer, Question

from .serializers import AnswerSerializer, QuestionSerializer


class QuestionsTagFilter(filters.BaseFilterBackend):
    """ Filter questions by specified tag.
    """

    def filter_queryset(self, request, queryset, view):
        tag = request.query_params.get("tag", "")
        tag = tag.strip().lower()

        if not tag:
            return queryset

        return queryset.filter(tags__name=tag)


class QuestionsOrderingFilter(filters.BaseFilterBackend):
    """ Ordering for questions.
    """

    VALID_SORTS = {
        "latest": "-posted",
        "popular": "-rating",
        "trending": "-number_of_votes",
    }

    def filter_queryset(self, request, queryset, view):
        sort = request.query_params.get("sort", "")
        sort = sort.strip().lower()

        if sort not in self.VALID_SORTS:
            return queryset

        return queryset.order_by(self.VALID_SORTS[sort])


class QuestionsAPIView(ListCreateAPIView):

    filter_backends = [
        QuestionsOrderingFilter,
        QuestionsTagFilter,
        filters.SearchFilter,
    ]
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ["title", "content"]
    serializer_class = QuestionSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = Question.objects.all()
        queryset = queryset.select_related("author")
        queryset = queryset.prefetch_related("tags")

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
