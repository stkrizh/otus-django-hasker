from django.shortcuts import get_object_or_404

from rest_framework import filters
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from questions.models import Answer, AnswerVote, Question, QuestionVote

from .permissions import IsOwnerOfQuestionOrReadOnly, IsOwnerOrReadOnly
from .serializers import (
    AnswerSerializer,
    AnswerDetailSerializer,
    AnswerVoteSerializer,
    QuestionSerializer,
    QuestionVoteSerializer,
)


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


class QuestionVotesAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = QuestionVoteSerializer

    def initial(self, request, *args, **kwargs):
        """
        Runs anything that needs to occur prior to calling the method handler.
        """
        super().initial(request, *args, **kwargs)
        self.question = get_object_or_404(Question, pk=self.kwargs.get("pk"))

    def get_queryset(self):
        queryset = QuestionVote.objects.all()
        queryset = queryset.select_related("user")
        queryset = queryset.filter(to=self.question)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, to=self.question)


class QuestionVoteDetailsAPIView(RetrieveUpdateDestroyAPIView):
    http_method_names = ["get", "patch", "delete", "head", "options"]
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = QuestionVoteSerializer

    def initial(self, request, *args, **kwargs):
        """
        Runs anything that needs to occur prior to calling the method handler.
        """
        super().initial(request, *args, **kwargs)
        self.question = get_object_or_404(
            Question, pk=self.kwargs.get("question_pk")
        )

    def get_queryset(self):
        queryset = QuestionVote.objects.filter(to=self.question)
        queryset = queryset.select_related("user")

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


class AnswerDetailsAPIView(RetrieveUpdateAPIView):
    http_method_names = ["get", "patch", "head", "options"]
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsOwnerOfQuestionOrReadOnly,
    ]
    serializer_class = AnswerDetailSerializer

    def get_queryset(self):
        queryset = Answer.objects.all()
        queryset = queryset.select_related("author")

        return queryset

    def perform_update(self, serializer):
        """ Mark / unmark answer as accepted one
        """
        answer = serializer.instance
        is_accepted_new = serializer.validated_data["is_accepted"]

        # Do nothing if `is_accepted` is not changed
        if answer.is_accepted == is_accepted_new:
            return

        if is_accepted_new:
            answer.mark()
        else:
            answer.unmark()


class AnswerVotesAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = AnswerVoteSerializer

    def initial(self, request, *args, **kwargs):
        """
        Runs anything that needs to occur prior to calling the method handler.
        """
        super().initial(request, *args, **kwargs)
        self.answer = get_object_or_404(Answer, pk=self.kwargs.get("pk"))

    def get_queryset(self):
        queryset = AnswerVote.objects.all()
        queryset = queryset.select_related("user")
        queryset = queryset.filter(to=self.answer)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, to=self.answer)


class AnswerVoteDetailsAPIView(RetrieveUpdateDestroyAPIView):
    http_method_names = ["get", "patch", "delete", "head", "options"]
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = AnswerVoteSerializer

    def initial(self, request, *args, **kwargs):
        """
        Runs anything that needs to occur prior to calling the method handler.
        """
        super().initial(request, *args, **kwargs)
        self.answer = get_object_or_404(
            Answer, pk=self.kwargs.get("answer_pk")
        )

    def get_queryset(self):
        queryset = AnswerVote.objects.filter(to=self.answer)
        queryset = queryset.select_related("user")

        return queryset
