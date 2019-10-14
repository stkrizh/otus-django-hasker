from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from questions.tests.fixtures import CreateDataMixin
from questions.models import Question


class QuestionsTests(CreateDataMixin, APITestCase):
    def test_questions_get(self):
        user = self.create_user()

        for _ in range(5):
            self.create_question(user)

        url = reverse("api_questions")
        response = self.client.get(url, format="json")
        data = response.json()

        count = Question.objects.count()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("count"), count)
        self.assertEqual(len(data.get("results", [])), count)

    def test_questions_get_search(self):
        user = self.create_user()
        questions = [self.create_question(user) for _ in range(5)]

        q = questions[2].title[:5]
        url = reverse("api_questions")

        response = self.client.get(url + f"?search={q}", format="json")
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("count"), 1)
        self.assertEqual(len(data.get("results", [])), 1)
        self.assertEqual(data["results"][0]["id"], questions[2].id)

    def test_questions_get_tag(self):
        user = self.create_user()
        questions = [self.create_question(user) for _ in range(5)]

        questions[2].add_tags(["aaa", "bbb"], user)
        questions[3].add_tags(["aaa", "ccc"], user)
        url = reverse("api_questions")

        response = self.client.get(url + f"?tag=aaa", format="json")
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("count"), 2)
        self.assertEqual(len(data.get("results", [])), 2)

        response = self.client.get(url + f"?tag=bbb", format="json")
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("count"), 1)
        self.assertEqual(len(data.get("results", [])), 1)

    def test_questions_post_unauthorized(self):
        url = reverse("api_questions")
        response = self.client.post(
            url,
            data={"content": "aaa", "title": "aaa", "tags": ["tag1", "tag2"]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_questions_post_authorized(self):
        url = reverse("api_questions")
        user = self.create_user()

        self.client.force_authenticate(user=user)
        response = self.client.post(
            url,
            data={"content": "aaa", "title": "bbb", "tags": ["tag1", "tag2"]},
            format="json",
        )
        data = response.json()

        question_id = data.get("id")
        username = data.get("author", {}).get("username")

        question = Question.objects.get(pk=question_id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(username, user.username)
        self.assertEqual(question.title, "bbb")
        self.assertEqual(question.content, "aaa")
        self.assertEqual(
            {"tag1", "tag2"}, {tag.name for tag in question.tags.all()}
        )

    def test_question_details(self):
        user = self.create_user()
        question = self.create_question(user)

        url = reverse("api_question_details", kwargs={"pk": question.pk})
        response = self.client.get(url, format="json")
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("author", {}).get("username"), user.username)
        self.assertEqual(data.get("content"), question.content)
        self.assertEqual(data.get("title"), question.title)

    def test_question_votes_get(self):
        user = self.create_user()
        question = self.create_question(user)

        voters = [self.create_user() for _ in range(3)]
        for voter, value in zip(voters, [1, -1, 1]):
            question.vote(voter, value)

        url = reverse("api_question_votes", kwargs={"pk": question.pk})
        response = self.client.get(url, format="json")
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("count"), 3)
        self.assertEqual(len(data.get("results", [])), 3)
        self.assertEqual(
            sum(item["value"] for item in data.get("results", [])), 1
        )

    def test_question_votes_post_unauthorized(self):
        user = self.create_user()
        question = self.create_question(user)

        url = reverse("api_question_votes", kwargs={"pk": question.pk})
        response = self.client.post(url, data={"value": 1}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_question_votes_post_authorized(self):
        user = self.create_user()
        question = self.create_question(user)

        voter = self.create_user()
        self.client.force_authenticate(user=voter)

        url = reverse("api_question_votes", kwargs={"pk": question.pk})
        response = self.client.post(url, data={"value": 1}, format="json")
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data.get("user", {}).get("id"), voter.id)
        self.assertEqual(data.get("value"), 1)

    def test_question_vote_change_unauthorized(self):
        question = self.create_question()

        voter = self.create_user()
        question.vote(voter, 1)
        vote = question.votes.first()

        url = reverse(
            "api_question_vote_details",
            kwargs={"question_pk": question.pk, "pk": vote.pk},
        )
        response = self.client.patch(url, data={"value": -1}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_question_vote_change_not_owner(self):
        question = self.create_question()

        voter = self.create_user()
        question.vote(voter, 1)
        vote = question.votes.first()

        other_user = self.create_user()
        self.client.force_authenticate(other_user)

        url = reverse(
            "api_question_vote_details",
            kwargs={"question_pk": question.pk, "pk": vote.pk},
        )
        response = self.client.patch(url, data={"value": -1}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_question_vote_change_owner(self):
        question = self.create_question()

        voter = self.create_user()
        question.vote(voter, 1)
        vote = question.votes.first()

        self.client.force_authenticate(voter)

        url = reverse(
            "api_question_vote_details",
            kwargs={"question_pk": question.pk, "pk": vote.pk},
        )
        response = self.client.patch(url, data={"value": -1}, format="json")
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("value"), -1)

        response = self.client.delete(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(question.votes.count(), 0)
