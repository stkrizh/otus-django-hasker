from itertools import combinations, islice
from string import ascii_lowercase
from typing import NamedTuple

from django.conf import settings
from django.test import SimpleTestCase, TestCase

from questions.forms import AskForm, VoteForm
from questions.models import Answer, Question

from .fixtures import CreateDataMixin


def random_tags(n: int) -> str:
    """ Returns comma-separated `n` tags.
    """
    items = ("".join(i) for i in combinations(ascii_lowercase, 3))
    return ", ".join(islice(items, n))


class AskFormCase(NamedTuple):
    title: str
    content: str
    tags: str


class TestAskForm(SimpleTestCase):
    invalid_cases = [
        AskFormCase(title="", content="", tags=""),
        AskFormCase(title=" ", content=" ", tags=" "),
        AskFormCase(title="title", content=" ", tags=" "),
        AskFormCase(title=" ", content="content", tags=" "),
        AskFormCase(title=" ", content=" ", tags="tags"),
        AskFormCase(
            title="a" * (settings.QUESTIONS_MAX_TITLE_LEN + 1),
            content="content",
            tags="tags",
        ),
    ]

    def test_invalid_form(self):
        for case in self.invalid_cases:
            with self.subTest(case=case):
                form = AskForm(data=case._asdict())
                self.assertFalse(form.is_valid())

    def test_number_of_tags(self):
        data = {"title": "title", "content": "content", "tags": "tags"}

        form = AskForm(data)
        self.assertTrue(form.is_valid())

        data["tags"] = random_tags(settings.QUESTIONS_MAX_NUMBER_OF_TAGS + 1)
        form = AskForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("tags", form.errors)

        data["tags"] = ["aaa"] * (settings.QUESTIONS_MAX_NUMBER_OF_TAGS + 1)
        form = AskForm(data)
        self.assertTrue(form.is_valid())


class TestVoteForm(CreateDataMixin, TestCase):
    def test_vote_for_answer(self):
        data = {"target_id": self.answer_1.pk, "value": 1}
        form = VoteForm(data=data, model=Answer)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["target"].pk, self.answer_1.pk)

        data["value"] = -1
        form = VoteForm(data=data, model=Answer)
        self.assertTrue(form.is_valid())

    def test_vote_for_answer_invalid_target_id(self):
        data = {"target_id": 1000, "value": 1}
        form = VoteForm(data=data, model=Answer)
        self.assertFalse(form.is_valid())
        self.assertIn("target_id", form.errors)

    def test_vote_for_answer_invalid_vote(self):
        data = {"target_id": self.answer_1.pk, "value": 0}
        form = VoteForm(data=data, model=Answer)
        self.assertFalse(form.is_valid())
        self.assertIn("value", form.errors)

    def test_vote_for_question(self):
        data = {"target_id": self.question.pk, "value": 1}
        form = VoteForm(data=data, model=Question)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["target"].pk, self.question.pk)

        data["value"] = -1
        form = VoteForm(data=data, model=Question)
        self.assertTrue(form.is_valid())
