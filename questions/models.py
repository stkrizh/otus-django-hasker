from typing import List, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from django.db.models.functions import Greatest


VOTE_UP = 1
VOTE_DOWN = -1
VOTE_CHOICES = ((VOTE_UP, "Vote Up"), (VOTE_DOWN, "Vote Down"))


User = get_user_model()


class AbstractPost(models.Model):
    """ Abstract model that defines common fields and methods
    for Question / Answer models.
    """

    vote_class: Optional[models.Model] = None

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        related_query_name="%(class)s",
    )
    content = models.TextField(blank=False)
    posted = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    class Meta:
        abstract = True
        ordering = ["-posted"]

    def vote(self, user, value: int) -> int:
        """ Add vote from `user` and return new rating.
        """
        assert self.vote_class is not None
        assert value in (VOTE_DOWN, VOTE_UP), value

        try:
            current = self.vote_class.objects.get(user=user, to=self)
        except ObjectDoesNotExist:
            self.vote_class.objects.create(user=user, to=self, value=value)
            return self.rating + value

        if current.value == value:
            return self.rating

        self.vote_class.objects.filter(to=self, user=user).delete()
        return self.rating + value


class AbstractVote(models.Model):
    """ Abstract model that represents user votes for questions and answers.
    """

    timestamp = models.DateTimeField(auto_now=True)
    value = models.SmallIntegerField(choices=VOTE_CHOICES)
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        related_query_name="%(class)s",
    )

    class Meta:
        abstract = True
        ordering = ["-timestamp"]
        unique_together = ["to", "user"]

    def __str__(self):
        return f"{self.user.username} {self.value:+d}"


class AnswerVote(AbstractVote):
    to = models.ForeignKey(
        "Answer",
        on_delete=models.CASCADE,
        related_name="votes",
        related_query_name="votes",
    )


class Answer(AbstractPost):
    vote_class = AnswerVote

    is_accepted = models.BooleanField(default=False)
    question = models.ForeignKey(
        "Question",
        on_delete=models.CASCADE,
        related_name="answers",
        related_query_name="answer",
    )

    def __str__(self):
        return f"{self.question.title} - {self.content[:50]} ..."

    def mark(self):
        """ Mark the answer as accepted.
        """
        self.question.answers.update(is_accepted=False)
        self.is_accepted = True
        self.save(update_fields=["is_accepted"])

    def unmark(self):
        """ Unmark acceptance from the answer.
        """
        self.is_accepted = False
        self.save(update_fields=["is_accepted"])


class QuestionVote(AbstractVote):
    to = models.ForeignKey(
        "Question",
        on_delete=models.CASCADE,
        related_name="votes",
        related_query_name="votes",
    )


class Question(AbstractPost):
    vote_class = QuestionVote

    title = models.CharField(
        blank=False, max_length=settings.QUESTIONS_MAX_TITLE_LEN
    )
    tags = models.ManyToManyField("Tag")

    def __str__(self):
        return self.title

    @classmethod
    def trending(cls, count: int = 5) -> models.QuerySet:
        """ Returns a query set of trending questions.
        """
        qs = cls.objects.annotate(votes_count=models.Count("votes"))
        return qs.order_by("-votes_count")[:count]

    def add_tags(self, tags: List[str], user) -> None:
        if self.pk is None:
            raise ValueError("Instance should be saved.")
        for raw_tag in tags:
            try:
                tag = Tag.objects.get(name=raw_tag)
            except ObjectDoesNotExist:
                tag = Tag.objects.create(added=user, name=raw_tag)

            self.tags.add(tag)


class Tag(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="added_tags",
        related_query_name="added_tag",
    )
    name = models.CharField(
        blank=False, max_length=settings.QUESTIONS_MAX_TAG_LEN
    )

    def __str__(self):
        return self.name
