from django.contrib.auth import get_user_model

from django.test import TestCase, Client
from django.urls import reverse


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


class TestLogIn(CreateDataMixin, TestCase):
    def test_GET_unauthorized(self):
        client = Client()
        response = client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("users/login.html")

    def test_GET_authorized(self):
        client = Client()
        client.login(username=TEST_USER, password=TEST_PASSWORD)
        response = client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertInHTML(
            "<p>You have already logged in.</p>", str(response.content)
        )
        self.assertInHTML("<h3>Log Out</h3>", str(response.content))

    def test_POST_authorized(self):
        client = Client()
        client.login(username=TEST_USER, password=TEST_PASSWORD)
        response = client.post(reverse("login"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("index"), response.url)

        response = client.post(reverse("login"), follow=True)

        self.assertRedirects(response, reverse("index"))
        self.assertInHTML(
            "<p>You have already logged in.</p>", str(response.content)
        )

    def test_POST_unauthorized(self):
        client = Client()
        response = client.post(
            reverse("login"),
            data={"username": TEST_USER, "password": TEST_PASSWORD},
            follow=True,
        )

        self.assertRedirects(response, reverse("index"))
        self.assertInHTML(
            "<p>You have succesfully logged in!</p>", str(response.content)
        )


class TestLogOut(CreateDataMixin, TestCase):
    def test_POST_unauthorized(self):
        client = Client()
        response = client.post(reverse("logout"), data={}, follow=True)

        self.assertRedirects(response, reverse("index"))
        self.assertInHTML(
            "<p>You are not authenticated!</p>", str(response.content)
        )

    def test_POST_authorized(self):
        client = Client()
        client.login(username=TEST_USER, password=TEST_PASSWORD)
        response = client.post(reverse("logout"), data={}, follow=True)

        self.assertRedirects(response, reverse("index"))
        self.assertInHTML(
            "<p>Goodbye! You have successfully logged out.</p>",
            str(response.content),
        )


class TestSignUp(CreateDataMixin, TestCase):
    def test_GET_unauthorized(self):
        client = Client()
        response = client.get(reverse("signup"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("users/signup.html")

    def test_GET_authorized(self):
        client = Client()
        client.login(username=TEST_USER, password=TEST_PASSWORD)
        response = client.get(reverse("signup"), follow=True)

        self.assertRedirects(response, reverse("index"))
        self.assertInHTML(
            "<p>You have already logged in.</p>", str(response.content)
        )

    def test_POST_authorized(self):
        client = Client()
        client.login(username=TEST_USER, password=TEST_PASSWORD)
        response = client.post(reverse("signup"), follow=True)

        self.assertRedirects(response, reverse("index"))
        self.assertInHTML(
            "<p>You have already logged in.</p>", str(response.content)
        )

    def test_POST_registration(self):
        client = Client()
        response = client.post(
            reverse("signup"),
            data={
                "username": "new_user",
                "email": "new_user_email@mail.fake",
                "password1": "new_password_123",
                "password2": "new_password_123",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("index"))
        self.assertInHTML(
            "<p>Thank you for registration!</p>", str(response.content)
        )

        self.assertTrue(
            self.user_model.objects.filter(username="new_user").exists()
        )


class TestSettings(CreateDataMixin, TestCase):
    def test_GET_unauthorized(self):
        client = Client()
        response = client.get(reverse("settings"))
        self.assertRedirects(
            response, reverse("login") + "?next=" + reverse("settings")
        )

    def test_GET_authorized(self):
        client = Client()
        client.login(username=TEST_USER, password=TEST_PASSWORD)
        response = client.get(reverse("settings"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("users/settings.html")

    def test_POST_unauthorized(self):
        client = Client()
        response = client.post(
            reverse("settings"), data={"email": "some_new_email@mail.fake"}
        )
        self.assertRedirects(
            response, reverse("login") + "?next=" + reverse("settings")
        )

    def test_POST_authorized(self):
        client = Client()
        client.login(username=TEST_USER, password=TEST_PASSWORD)
        response = client.post(
            reverse("settings"),
            data={"email": "some_new_email@mail.fake"},
            follow=True,
        )
        self.assertRedirects(response, reverse("settings"))
        self.assertInHTML(
            "<p>Your settings have been successfully updated!</p>",
            str(response.content),
        )

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "some_new_email@mail.fake")
