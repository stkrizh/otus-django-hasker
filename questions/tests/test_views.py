from hashlib import md5
from os import urandom

from django.test import TestCase, Client
from django.urls import reverse

from questions.models import Answer, AnswerVote, Question, QuestionVote

from .fixtures import CreateDataMixin, TEST_USER, TEST_PASSWORD


class TestAskView(CreateDataMixin, TestCase):
    def test_GET_unauthorised(self):
        client = Client()
        response = client.get(reverse("ask"))
        self.assertEqual(response.status_code, 302)

    def test_GET_authorised(self):
        client = Client()
        client.login(username=TEST_USER, password=TEST_PASSWORD)
        response = client.get(reverse("ask"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ask.html")

    def test_POST_unauthorized(self):
        client = Client()
        response = client.post(
            reverse("ask"), data={"title": "Title", "content": "Content"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_POST_authorized(self):
        client = Client()
        client.login(username=TEST_USER, password=TEST_PASSWORD)

        before_questions_count = Question.objects.count()
        response = client.post(
            reverse("ask"), data={"title": "Title", "content": "Content"}
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/", response.url)
        self.assertEqual(before_questions_count + 1, Question.objects.count())


class TestQuestionDetail(CreateDataMixin, TestCase):
    def test_GET_unauthorized(self):
        client = Client()
        response = client.get(
            reverse(
                "question_detail", kwargs={"question_id": self.question.pk}
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("answers.html")

    def test_GET_authorized(self):
        client = Client()
        client.login(username=TEST_USER, password=TEST_PASSWORD)
        response = client.get(
            reverse(
                "question_detail", kwargs={"question_id": self.question.pk}
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("answers.html")
        self.assertInHTML("<h3>Your answer</h3>", str(response.content))

    def test_POST_unauthorized(self):
        client = Client()
        response = client.post(
            reverse(
                "question_detail", kwargs={"question_id": self.question.pk}
            ),
            data={"content": "New answer!"},
        )
        self.assertEqual(response.status_code, 403)

    def test_POST_authorized(self):
        client = Client()
        client.login(username=TEST_USER, password=TEST_PASSWORD)

        url = reverse(
            "question_detail", kwargs={"question_id": self.question.pk}
        )

        unique = md5(urandom(10)).hexdigest()
        response = client.post(url, data={"content": unique})
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response.url)

        answer = Answer.objects.get(content=unique)
        self.assertEqual(self.question, answer.question)


class TestQuestionSearch(CreateDataMixin, TestCase):
    def test_empty_query(self):
        client = Client()
        url = reverse("search")
        response = client.get(url, data={"q": ""})
        self.assertEqual(response.status_code, 404)

    def test_search(self):
        unique_title = md5(urandom(10)).hexdigest()
        unique_content = md5(urandom(10)).hexdigest()

        self.question.title = unique_title
        self.question.content = unique_content
        self.question.save()

        client = Client()
        url = reverse("search")
        response = client.get(url, data={"q": f" foo {unique_title} bar "})
        self.assertEqual(response.status_code, 200)
        self.assertInHTML(
            f'<p class="wrapword">{unique_content}</p>', str(response.content)
        )

    def test_query_with_tag(self):
        unique_title = md5(urandom(10)).hexdigest()
        unique_content = md5(urandom(10)).hexdigest()
        unique_tag = md5(urandom(10)).hexdigest()

        question = Question(
            title=unique_title, content=unique_content, author=self.user
        )
        question.save()
        question.add_tags([unique_tag], self.user)

        client = Client()
        url = reverse("search")

        response = client.get(url, data={"q": f"tag:{unique_tag}"})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("tag", args=(unique_tag,)), response.url)

        response = client.get(
            url, data={"q": f"tag:{unique_tag}"}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertInHTML(
            f'<p class="wrapword">{unique_content}</p>', str(response.content)
        )


class TestVote(CreateDataMixin, TestCase):
    models = {"question": QuestionVote, "answer": AnswerVote}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.answer = cls.answer_1

    def test_GET_unauthorized(self):
        for model_name in self.models:
            with self.subTest(model_name=model_name):
                client = Client()
                response = client.get(
                    reverse(f"vote_{model_name}"),
                    data={
                        "target_id": getattr(self, model_name).pk,
                        "value": 1,
                    },
                )
                self.assertEqual(response.status_code, 403)

    def test_GET_authorized(self):
        for model_name in self.models:
            with self.subTest(model_name=model_name):
                client = Client()
                client.login(username=TEST_USER, password=TEST_PASSWORD)
                response = client.get(
                    reverse(f"vote_{model_name}"),
                    data={
                        "target_id": getattr(self, model_name).pk,
                        "value": 1,
                    },
                )
                self.assertEqual(response.status_code, 405)

    def test_POST_unauthorized(self):
        for model_name in self.models:
            with self.subTest(model_name=model_name):
                client = Client()
                response = client.post(
                    reverse(f"vote_{model_name}"),
                    data={
                        "target_id": getattr(self, model_name).pk,
                        "value": 1,
                    },
                )
                self.assertEqual(response.status_code, 403)

    def test_POST_authorized_invalid(self):
        for model_name in self.models:
            with self.subTest(model_name=model_name):
                client = Client()
                client.login(username=TEST_USER, password=TEST_PASSWORD)
                response = client.post(
                    reverse(f"vote_{model_name}"),
                    data={"target_id": 777, "value": 1},
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn("target_id", response.json())

    def test_POST_authorized_valid(self):
        for model_name, model in self.models.items():
            with self.subTest(model_name=model_name, model=model):
                self.assertFalse(
                    model.objects.filter(
                        to=getattr(self, model_name), user=self.user
                    ).exists()
                )

                client = Client()
                client.login(username=TEST_USER, password=TEST_PASSWORD)
                response = client.post(
                    reverse(f"vote_{model_name}"),
                    data={
                        "target_id": getattr(self, model_name).pk,
                        "value": 1,
                    },
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["rating"], 1)
                self.assertTrue(
                    model.objects.filter(
                        to=getattr(self, model_name), user=self.user
                    ).exists()
                )


class TestAnswerMark(CreateDataMixin, TestCase):
    def test_GET_unauthorized(self):
        client = Client()
        response = client.get(
            reverse(f"answer_mark", args=(self.answer_1.pk,)),
            data={},
        )
        self.assertEqual(response.status_code, 405)

    def test_POST_unauthorized(self):
        client = Client()
        response = client.post(
            reverse(f"answer_mark", args=(self.answer_1.pk,)),
            data={},
        )
        self.assertEqual(response.status_code, 403)

    def test_invalid_answer_id(self):
        client = Client()
        client.login(username=TEST_USER, password=TEST_PASSWORD)
        response = client.post(
            reverse(f"answer_mark", args=(777,)),
            data={},
        )
        self.assertEqual(response.status_code, 404)

    def test_not_owner(self):
        other_user = self.user_model(
            username="other_user",
            email="other_user@mail.fake"
        )
        other_user.set_password("other_user_password_123")
        other_user.save()

        self.assertNotEqual(other_user, self.answer_1.question.author)

        client = Client()
        client.login(username="other_user", password="other_user_password_123")
        response = client.post(
            reverse(f"answer_mark", args=(self.answer_1.pk,)),
            data={},
        )
        self.assertEqual(response.status_code, 403)

    def test_valid(self):
        before = self.answer_1.is_accepted

        client = Client()
        client.login(username=TEST_USER, password=TEST_PASSWORD)
        response = client.post(
            reverse(f"answer_mark", args=(self.answer_1.pk,)),
            data={},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["accepted"], not before)

        self.answer_1.referesh_from_db()
        self.assertEqual(self.answer_1.is_accepted, not before)
