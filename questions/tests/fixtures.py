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
            username=TEST_USER,
            email="test_user@mail.fake",
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
