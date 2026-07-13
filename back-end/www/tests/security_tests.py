"""Regression tests for the user enumeration / IDOR fix.

These tests exercise the controllers at the HTTP layer (unlike the other test
modules, which test the model_operations layer directly). They verify that
user-scoped read endpoints require the requester to be the owner or an admin,
and that public answer lists no longer leak user_id.
"""

from basic_tests import BasicTest
from controllers import root
from controllers import answer_controller
from controllers import vision_controller
from controllers import game_controller
from models.model_operations import scenario_operations
from models.model_operations import topic_operations
from models.model_operations import question_operations
from models.model_operations import answer_operations
from models.model_operations import user_operations
from models.model_operations import vision_operations
from models.model import db
from util.util import encode_jwt
from config.config import TestingConfig
from flask import Flask
import time
import json
import unittest


class SecurityTest(BasicTest):
    """Test case for the user enumeration / IDOR fix on user-scoped reads."""

    def create_app(self):
        # Register the controllers under test in addition to the root blueprint.
        app = Flask(__name__)
        app.register_blueprint(root.bp)
        app.register_blueprint(answer_controller.bp, url_prefix="/answer")
        app.register_blueprint(vision_controller.bp, url_prefix="/vision")
        app.register_blueprint(game_controller.bp, url_prefix="/game")
        app.config.from_object("config.config.TestingConfig")
        db.init_app(app)
        return app

    def setUp(self):
        db.create_all()

        self.topic = topic_operations.create_topic("test", "test")
        self.scenario_1 = scenario_operations.create_scenario(
            "t1", "d1", "i1", self.topic.id)

        multi_choices = [{"text": "a", "value": 1}, {"text": "b", "value": 2}]
        self.choice_question = question_operations.create_multi_choice_question(
            "text", choices=multi_choices, scenario_id=self.scenario_1.id)

        # user_1 is the "owner"; user_2 is an unrelated normal user.
        self.user_1 = user_operations.create_user("user1")
        self.user_2 = user_operations.create_user("user2")

        # Give user_1 an answer (tied to scenario_1) and a vision.
        self.answer_1 = answer_operations.create_choice_answer(
            choices=self.choice_question.choices[0].id,
            user_id=self.user_1.id, question_id=self.choice_question.id)

        self.mood = vision_operations.create_mood("happy")
        # Use a VIDEO media (with url, no unsplash fields) to keep the fixture
        # simple; IMAGE media would require unsplash_image_id and friends.
        medias = [{"url": "http://img", "description": "d", "type": "VIDEO"}]
        self.vision_1 = vision_operations.create_vision(
            mood_id=self.mood.id, medias=medias,
            user_id=self.user_1.id, scenario_id=self.scenario_1.id)

    def _token(self, user_id, client_type):
        """Build a valid user JWT for the given user_id and client_type."""
        now = int(time.time())
        payload = {
            "user_id": user_id,
            "client_type": client_type,
            "iat": now,
            "exp": now + 3600,
            "iss": "test",
            "jti": "test",
        }
        return encode_jwt(payload, TestingConfig.JWT_PRIVATE_KEY)

    # -- vision -------------------------------------------------------------

    def test_vision_by_user_requires_token(self):
        r = self.client.get("/vision/?paginate=0&user_id=%d" % self.user_1.id)
        self.assertEqual(r.status_code, 400)  # missing user_token

    def test_vision_by_user_forbidden_for_non_owner(self):
        token = self._token(self.user_2.id, 1)
        r = self.client.get("/vision/?paginate=0&user_id=%d&user_token=%s"
                            % (self.user_1.id, token))
        self.assertEqual(r.status_code, 403)

    def test_vision_by_user_ok_for_owner(self):
        token = self._token(self.user_1.id, 1)
        r = self.client.get("/vision/?paginate=0&user_id=%d&user_token=%s"
                            % (self.user_1.id, token))
        self.assertEqual(r.status_code, 200)

    def test_vision_by_user_ok_for_admin(self):
        token = self._token(self.user_2.id, 0)  # admin viewing another user
        r = self.client.get("/vision/?paginate=0&user_id=%d&user_token=%s"
                            % (self.user_1.id, token))
        self.assertEqual(r.status_code, 200)

    # -- answer -------------------------------------------------------------

    def test_answer_by_user_requires_token(self):
        r = self.client.get("/answer/?user_id=%d" % self.user_1.id)
        self.assertEqual(r.status_code, 400)

    def test_answer_by_user_forbidden_for_non_owner(self):
        token = self._token(self.user_2.id, 1)
        r = self.client.get("/answer/?user_id=%d&user_token=%s"
                            % (self.user_1.id, token))
        self.assertEqual(r.status_code, 403)

    def test_answer_by_user_ok_for_owner(self):
        token = self._token(self.user_1.id, 1)
        r = self.client.get("/answer/?user_id=%d&user_token=%s"
                            % (self.user_1.id, token))
        self.assertEqual(r.status_code, 200)

    def test_public_answer_list_hides_user_id(self):
        # The public per-scenario list must not leak the author's user_id.
        r = self.client.get("/answer/?scenario_id=%d" % self.scenario_1.id)
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)["data"]
        self.assertTrue(len(data) >= 1)
        for item in data:
            self.assertNotIn("user_id", item)

    # -- game ---------------------------------------------------------------

    def test_game_by_user_requires_token(self):
        r = self.client.get("/game/?user_id=%d" % self.user_1.id)
        self.assertEqual(r.status_code, 400)

    def test_game_by_user_forbidden_for_normal_user(self):
        # Game reads are admin-only, so even the owner (non-admin) is denied.
        token = self._token(self.user_1.id, 1)
        r = self.client.get("/game/?user_id=%d&user_token=%s"
                            % (self.user_1.id, token))
        self.assertEqual(r.status_code, 403)

    def test_game_by_user_ok_for_admin(self):
        token = self._token(self.user_2.id, 0)
        r = self.client.get("/game/?user_id=%d&user_token=%s"
                            % (self.user_1.id, token))
        self.assertEqual(r.status_code, 200)

    def test_game_list_requires_admin(self):
        r = self.client.get("/game/")
        self.assertEqual(r.status_code, 400)


if __name__ == "__main__":
    unittest.main()
