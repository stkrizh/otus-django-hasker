from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from questions.tests.fixtures import CreateDataMixin
from questions.models import Answer, Question


class AnswersTests(CreateDataMixin, APITestCase):
    def test_answers_get(self):
        author = self.create_user()
        question = self.create_question(user=author)
        users = [self.create_user() for _ in range(5)]

        for user in users:
            self.create_answer(question, user)

        url = reverse("api_answers", kwargs={"pk": question.pk})
        response = self.client.get(url, format="json")
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("count"), 5)
        self.assertEqual(len(data.get("results", [])), 5)
        self.assertEqual(
            {item["author"]["username"] for item in data.get("results", [])},
            {user.username for user in users},
        )

    def test_answers_post_unauthorized(self):
        author = self.create_user()
        question = self.create_question(user=author)

        url = reverse("api_answers", kwargs={"pk": question.pk})
        response = self.client.post(
            url, data={"content": "aaa"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_answers_post_authorized(self):
        author = self.create_user()
        question = self.create_question(user=author)

        user = self.create_user()
        self.client.force_authenticate(user=user)

        url = reverse("api_answers", kwargs={"pk": question.pk})
        response = self.client.post(
            url, data={"content": "aaa"}, format="json"
        )
        data = response.json()

        answer_id = data.get("id")
        answer = Answer.objects.get(pk=answer_id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(question.answers.count(), 1)
        self.assertEqual(answer.author.username, user.username)
        self.assertEqual(answer.content, "aaa")

    def test_answer_vote_change_unauthorized(self):
        answer = self.create_answer()

        voter = self.create_user()
        answer.vote(voter, 1)
        vote = answer.votes.first()

        url = reverse(
            "api_answer_vote_details",
            kwargs={"answer_pk": answer.pk, "pk": vote.pk},
        )
        response = self.client.patch(url, data={"value": -1}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_answer_vote_change_not_owner(self):
        answer = self.create_answer()

        voter = self.create_user()
        answer.vote(voter, 1)
        vote = answer.votes.first()

        other_user = self.create_user()
        self.client.force_authenticate(other_user)

        url = reverse(
            "api_answer_vote_details",
            kwargs={"answer_pk": answer.pk, "pk": vote.pk},
        )
        response = self.client.patch(url, data={"value": -1}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_answer_vote_change_owner(self):
        answer = self.create_answer()

        voter = self.create_user()
        answer.vote(voter, 1)
        vote = answer.votes.first()

        self.client.force_authenticate(voter)

        url = reverse(
            "api_answer_vote_details",
            kwargs={"answer_pk": answer.pk, "pk": vote.pk},
        )
        response = self.client.patch(url, data={"value": -1}, format="json")
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("value"), -1)

        response = self.client.delete(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(answer.votes.count(), 0)

    def test_accept_answer_unauthorized(self):
        question_author = self.create_user()
        question = self.create_question(user=question_author)
        answers = [self.create_answer(question=question) for _ in range(3)]

        url = reverse("api_answer_details", kwargs={"pk": answers[1].pk})
        response = self.client.patch(
            url, data={"is_accepted": True}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_accept_answer_not_question_owner(self):
        question_author = self.create_user()
        question = self.create_question(user=question_author)
        answers = [self.create_answer(question=question) for _ in range(3)]

        other_user = self.create_user()
        self.client.force_authenticate(other_user)

        url = reverse("api_answer_details", kwargs={"pk": answers[1].pk})
        response = self.client.patch(
            url, data={"is_accepted": True}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_accept_answer_question_owner(self):
        question_author = self.create_user()
        question = self.create_question(user=question_author)
        answers = [self.create_answer(question=question) for _ in range(3)]

        self.client.force_authenticate(question_author)

        url = reverse("api_answer_details", kwargs={"pk": answers[1].pk})
        response = self.client.patch(
            url, data={"is_accepted": True}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Answer.objects.get(question=question, is_accepted=True).pk,
            answers[1].pk,
        )

        url = reverse("api_answer_details", kwargs={"pk": answers[2].pk})
        response = self.client.patch(
            url, data={"is_accepted": True}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Answer.objects.get(question=question, is_accepted=True).pk,
            answers[2].pk,
        )
