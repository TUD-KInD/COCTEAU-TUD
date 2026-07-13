"""Schema for object serialization and deserialization."""

from flask_marshmallow import Marshmallow
from marshmallow_enum import EnumField
from models.model import Topic
from models.model import Scenario
from models.model import Question
from models.model import QuestionTypeEnum
from models.model import Choice
from models.model import User
from models.model import Vision
from models.model import Media
from models.model import MediaTypeEnum
from models.model import Mood
from models.model import Answer
from models.model import Game
from models.model import GameStatusEnum
from models.model import Guess


# Use Marshmallow to simplify object–relational mapping
ma = Marshmallow()


class ChoiceSchema(ma.Schema):
    """The schema for the Choice table, used for jsonify."""
    class Meta:
        model = Choice
        fields = ("id", "text", "value")
choices_schema = ChoiceSchema(many=True)


class QuestionSchema(ma.Schema):
    """The schema for the Question table, used for jsonify."""
    question_type = EnumField(QuestionTypeEnum)
    choices = ma.Nested(choices_schema)
    class Meta:
        model = Question
        fields = ("id", "text", "question_type", "scenario_id", "topic_id",
                "choices", "order", "page", "shuffle_choices")
question_schema = QuestionSchema()
questions_schema = QuestionSchema(many=True)


class TopicSchema(ma.Schema):
    """The schema for the Topic table, used for jsonify."""
    questions = ma.Nested(questions_schema)
    class Meta:
        model = Topic # the class for the model
        fields = ("id", "title", "description", "questions") # fields to expose
topic_schema = TopicSchema()
topics_schema = TopicSchema(many=True)


class ScenarioSchema(ma.Schema):
    """The schema for the Scenario table, used for jsonify."""
    questions = ma.Nested(questions_schema)
    class Meta:
        model = Scenario
        fields = ("id", "title", "description", "image", "topic_id", "mode", "view")
scenario_schema = ScenarioSchema()
scenarios_schema = ScenarioSchema(many=True)


class UserSchema(ma.Schema):
    """The schema for the User table, used for jsonify."""
    class Meta:
        model = User
        fields = ("id", "created_at", "client_id", "client_type")
user_schema = UserSchema()
users_schema = UserSchema(many=True)


class MoodSchema(ma.Schema):
    """The schema for the Mood table, used for jsonify."""
    class Meta:
        model = Mood
        fields = ("id", "name", "image", "order")
mood_schema = MoodSchema()
moods_schema = MoodSchema(many=True)


class MediaSchema(ma.Schema):
    """The schema for the Media table, used for jsonify."""
    media_type = EnumField(MediaTypeEnum)
    class Meta:
        model = Media
        fields = ("id", "url", "unsplash_creator_name", "unsplash_creator_url",
                "description", "vision_id", "unsplash_image_id", "media_type")
media_schema = MediaSchema()
medias_schema = MediaSchema(many=True)


class VisionSchema(ma.Schema):
    """The schema for the Vision table, used for jsonify."""
    medias = ma.Nested(medias_schema)
    class Meta:
        model = Vision
        fields = ("id", "scenario_id", "medias")
vision_schema = VisionSchema()
visions_schema = VisionSchema(many=True)


class VisionMoodSchema(ma.Schema):
    """The schema for the Vision table to get the mood, used for jsonify."""
    class Meta:
        model = Vision
        fields = ("id", "mood_id")
vision_mood_schema = VisionMoodSchema()
visions_mood_schema = VisionMoodSchema(many=True)


class AnswerSchema(ma.Schema):
    """The schema for the Answer table, used for jsonify.

    Note: user_id is deliberately omitted from this public schema to avoid
    leaking which user authored each answer (a user enumeration vector on the
    public per-scenario/topic/question answer lists). Admin responses use
    AnswerAdminSchema below, which includes user_id.
    """
    choices = ma.Nested(choices_schema)
    class Meta:
        model = Answer
        fields = ("id", "text", "question_id", "choices")
answer_schema = AnswerSchema()
answers_schema = AnswerSchema(many=True)


class AnswerAdminSchema(ma.Schema):
    """The schema for the Answer table for admin users, used for jsonify."""
    choices = ma.Nested(choices_schema)
    class Meta:
        model = Answer
        fields = ("id", "text", "user_id", "question_id", "choices", "secret")
answer_admin_schema = AnswerAdminSchema()
answers_admin_schema = AnswerAdminSchema(many=True)


class GuessSchema(ma.Schema):
    """The schema for the Guess table, used for jsonify."""
    class Meta:
        model = Guess
        fields = ("id", "game_id", "mood_id")
guess_schema = GuessSchema()
guesses_schema = GuessSchema(many=True)


class GameSchema(ma.Schema):
    """The schema for the Game table, used for jsonify."""
    status = EnumField(GameStatusEnum)
    guesses = ma.Nested(guesses_schema)
    class Meta:
        model = Game
        fields = ("id", "start_time", "end_time", "status", "feedback",
                "vision_id", "user_id", "guesses")
game_schema = GameSchema()
games_schema = GameSchema(many=True)
