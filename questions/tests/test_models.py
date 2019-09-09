from django.test import TestCase

from questions.models import (
    VOTE_UP,
    VOTE_DOWN,
    Answer,
    AnswerVote,
    Question,
    QuestionVote,
)

from .fixtures import CreateDataMixin


class TestAnswer(CreateDataMixin, TestCase):
    def test_mark(self):
        self.answer_1.mark()
        self.assertTrue(self.answer_1.is_accepted)
        self.assertFalse(self.answer_2.is_accepted)

        self.answer_2.mark()
        self.answer_1.refresh_from_db()
        self.assertTrue(self.answer_2.is_accepted)
        self.assertFalse(self.answer_1.is_accepted)

    def test_unmark(self):
        self.answer_1.mark()
        self.answer_2.refresh_from_db()
        self.assertTrue(self.answer_1.is_accepted)
        self.assertFalse(self.answer_2.is_accepted)

        self.answer_1.unmark()
        self.answer_2.refresh_from_db()
        self.assertFalse(self.answer_1.is_accepted)
        self.assertFalse(self.answer_2.is_accepted)


class TestAnswerVote(CreateDataMixin, TestCase):
    def test_answer_vote(self):
        rating_0 = self.answer_1.vote(self.user, VOTE_UP)
        self.answer_1.refresh_from_db()
        self.assertEqual(rating_0, self.answer_1.rating)

        rating_1 = self.answer_1.vote(self.user, VOTE_UP)
        self.answer_1.refresh_from_db()
        self.assertEqual(rating_1, self.answer_1.rating)
        self.assertEqual(rating_1, rating_0)

        rating_2 = self.answer_1.vote(self.user, VOTE_DOWN)
        self.answer_1.refresh_from_db()
        self.assertEqual(rating_2, self.answer_1.rating)
        self.assertEqual(rating_2, rating_1 - 1)
        self.assertFalse(AnswerVote.objects.exists())

        rating_3 = self.answer_1.vote(self.user, VOTE_DOWN)
        self.answer_1.refresh_from_db()
        self.assertEqual(rating_3, self.answer_1.rating)
        self.assertEqual(rating_3, rating_2 - 1)

        rating_4 = self.answer_1.vote(self.user, VOTE_UP)
        self.answer_1.refresh_from_db()
        self.assertEqual(rating_4, self.answer_1.rating)
        self.assertEqual(rating_4, 0)

    def test_rating_signals(self):
        self.answer_2.refresh_from_db()
        rating = self.answer_2.rating
        vote = AnswerVote.objects.create(
            to=self.answer_2, user=self.user, value=VOTE_UP
        )
        self.answer_2.refresh_from_db()
        self.assertEqual(self.answer_2.rating, rating + 1)

        AnswerVote.objects.filter(pk=vote.pk).delete()
        self.answer_2.refresh_from_db()
        self.assertEqual(self.answer_2.rating, rating)

        vote = AnswerVote.objects.create(
            to=self.answer_2, user=self.user, value=VOTE_DOWN
        )
        self.answer_2.refresh_from_db()
        self.assertEqual(self.answer_2.rating, rating - 1)

        vote.value = VOTE_UP
        vote.save(update_fields=["value"])
        self.answer_2.refresh_from_db()
        self.assertEqual(self.answer_2.rating, rating + 1)


class TestQuestion(CreateDataMixin, TestCase):
    def test_trending(self):
        users = [
            self.user_model(username="user1", email="user1@mail.fake"),
            self.user_model(username="user2", email="user2@mail.fake"),
            self.user_model(username="user3", email="user3@mail.fake"),
            self.user_model(username="user4", email="user4@mail.fake"),
        ]
        self.user_model.objects.bulk_create(users)

        questions = [
            Question(author=users[0], title="A0", content="B0"),
            Question(author=users[1], title="A1", content="B1"),
            Question(author=users[2], title="A2", content="B2"),
        ]
        Question.objects.bulk_create(questions)

        questions[2].vote(users[0], VOTE_UP)
        questions[2].vote(users[1], VOTE_DOWN)

        questions[1].vote(users[0], VOTE_UP)
        questions[1].vote(users[1], VOTE_DOWN)
        questions[1].vote(users[2], VOTE_DOWN)
        questions[1].vote(users[3], VOTE_DOWN)

        questions[0].vote(users[1], VOTE_DOWN)
        questions[0].vote(users[2], VOTE_DOWN)
        questions[0].vote(users[3], VOTE_DOWN)

        trending_questions = list(Question.trending(3))
        self.assertEqual(3, len(trending_questions))
        self.assertEqual(questions[1].pk, trending_questions[0].pk)
        self.assertEqual(questions[0].pk, trending_questions[1].pk)
        self.assertEqual(questions[2].pk, trending_questions[2].pk)

    def test_add_tags(self):
        question = Question(author=self.user, title="aaa", content="bbb")

        with self.assertRaises(ValueError):
            question.add_tags(["tag1", "tag2"], self.user)

        question.save()
        raw_tags = ["tag1", "tag2", "tag3"]
        question.add_tags(raw_tags, self.user)

        self.assertEqual(
            set(raw_tags), set(question.tags.values_list("name", flat=True))
        )


class TestQuestionVote(CreateDataMixin, TestCase):
    def test_question_vote(self):
        rating_0 = self.question.vote(self.user, VOTE_UP)
        self.question.refresh_from_db()
        self.assertEqual(rating_0, self.question.rating)

        rating_1 = self.question.vote(self.user, VOTE_UP)
        self.question.refresh_from_db()
        self.assertEqual(rating_1, self.question.rating)
        self.assertEqual(rating_1, rating_0)

        rating_2 = self.question.vote(self.user, VOTE_DOWN)
        self.question.refresh_from_db()
        self.assertEqual(rating_2, self.question.rating)
        self.assertEqual(rating_2, rating_1 - 1)
        self.assertFalse(AnswerVote.objects.exists())

        rating_3 = self.question.vote(self.user, VOTE_DOWN)
        self.question.refresh_from_db()
        self.assertEqual(rating_3, self.question.rating)
        self.assertEqual(rating_3, rating_2 - 1)

        rating_4 = self.question.vote(self.user, VOTE_UP)
        self.question.refresh_from_db()
        self.assertEqual(rating_4, self.question.rating)
        self.assertEqual(rating_4, 0)

    def test_rating_signals(self):
        self.question.refresh_from_db()
        rating = self.question.rating
        vote = QuestionVote.objects.create(
            to=self.question, user=self.user, value=VOTE_UP
        )
        self.question.refresh_from_db()
        self.assertEqual(self.question.rating, rating + 1)

        QuestionVote.objects.filter(pk=vote.pk).delete()
        self.question.refresh_from_db()
        self.assertEqual(self.question.rating, rating)

        vote = QuestionVote.objects.create(
            to=self.question, user=self.user, value=VOTE_DOWN
        )
        self.question.refresh_from_db()
        self.assertEqual(self.question.rating, rating - 1)

        vote.value = VOTE_UP
        vote.save(update_fields=["value"])
        self.question.refresh_from_db()
        self.assertEqual(self.question.rating, rating + 1)
