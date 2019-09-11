from hashlib import md5
from os import urandom

from django.contrib.auth import get_user_model

from questions.models import Answer, Question


TEST_USER = "test_user"
TEST_PASSWORD = "test_password_123"


class CreateDataMixin:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_model = get_user_model()

        cls.user = cls.user_model(
            username=TEST_USER, email="test_user@mail.fake"
        )
        cls.user.set_password(TEST_PASSWORD)
        cls.user.save()

        cls.question = Question.objects.create(
            author=cls.user, title="Title", content="Content"
        )
        cls.answer_1 = Answer.objects.create(
            author=cls.user, question=cls.question, content="Content 1"
        )
        cls.answer_2 = Answer.objects.create(
            author=cls.user, question=cls.question, content="Content 2"
        )

    @classmethod
    def create_user(cls):
        user = cls.user_model(
            username=md5(urandom(10)).hexdigest(),
            email=f"{md5(urandom(10)).hexdigest()}@mail.fake",
        )
        user.set_password(md5(urandom(10)).hexdigest())
        user.save()
        return user

    @classmethod
    def create_question(cls, user=None):
        if user is None:
            user = cls.user

        question = Question.objects.create(
            author=user,
            title=md5(urandom(10)).hexdigest(),
            content=md5(urandom(10)).hexdigest(),
        )
        return question

    @classmethod
    def create_answer(cls, question=None, user=None):
        if user is None:
            user = cls.user

        if question is None:
            question = cls.question

        answer = Answer.objects.create(
            author=user,
            question=question,
            content=md5(urandom(10)).hexdigest(),
        )
        return answer
