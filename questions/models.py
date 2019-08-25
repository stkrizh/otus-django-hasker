from django.db import models


class AbstractPost(models.Model):
    """ Abstract model that defines common fields and methods
    for Question / Answer models.
    """

    author = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        related_query_name="%(class)s",
    )
    content = models.TextField(blank=False)
    posted = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ["-posted"]


class AbstractVote(models.Model):
    """ Abstract model that represents user votes for questions and answers.
    """

    VOTE_TYPES = ((+1, "Vote Up"), (-1, "Vote Down"))

    timestamp = models.DateTimeField(auto_now=True)
    type = models.SmallIntegerField(choices=VOTE_TYPES)
    user = models.ForeignKey(
        to="users.User",
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        related_query_name="%(class)s",
    )

    class Meta:
        abstract = True
        ordering = ["-timestamp"]


class Answer(AbstractPost):
    is_accepted = models.BooleanField(default=False)
    question = models.ForeignKey(
        "Question",
        on_delete=models.CASCADE,
        related_name="answers",
        related_query_name="answer",
    )


class AnswerVote(AbstractVote):
    to = models.ForeignKey(
        "Answer",
        on_delete=models.CASCADE,
        related_name="votes",
        related_query_name="vote",
    )


class Question(AbstractPost):
    title = models.CharField(blank=False, max_length=255)


class QuestionVote(AbstractVote):
    to = models.ForeignKey(
        "Question",
        on_delete=models.CASCADE,
        related_name="votes",
        related_query_name="vote",
    )
