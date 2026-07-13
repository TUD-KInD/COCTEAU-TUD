"""The controller for https://[PATH]/game/"""

from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from util.util import InvalidUsage
from util.util import handle_invalid_usage
from util.util import decode_user_token
from util.util import try_wrap_response
from config.config import config
from models.model_operations.game_operations import create_random_game
from models.model_operations.game_operations import submit_game
from models.model_operations.game_operations import get_game_by_id
from models.model_operations.game_operations import get_games_by_user
from models.model_operations.game_operations import get_games_by_vision
from models.model_operations.game_operations import get_all_games
from models.model_operations.game_operations import remove_game
from models.model_operations.vision_operations import get_vision_by_id
from models.schema import game_schema
from models.schema import games_schema
from models.schema import vision_schema
from models.schema import vision_mood_schema


bp = Blueprint("game_controller", __name__)


@bp.route("/", methods=["GET", "POST", "PATCH", "DELETE"])
def game():
    """
    The function for operating the Game table.

    Parameters
    ----------
    user_token : str
        The encoded user JWT, issued by the back-end.
        (required for POST, PATCH, and DELETE)
    game_id : int
        ID of the game.
        (optional for GET)
        (required for PATCH and DELETE)
    vision_id: int
        Vision ID of the game.
        (optional for GET)
    user_id : int
        ID of the user that plays the game(s).
        (optional for GET)
    scenario_id : int
        ID of the scenario to choose the vision for the game.
        (optional for POST)
    feedback : str
        Feedback text of the vision in the game.
        (optional for PATCH)
    moods : list of int
        List of mood IDs that the user guesses.
        (optional for PATCH)

    Returns
    -------
    Game or list of Game
        The retrieved game object.
        Or a list of retrieved game objects.
    """
    rj = request.json

    # Sanity and permission check
    # GET operations expose the user_id behind each game and are only used by
    # the admin dashboard, so they require an admin token. This prevents
    # unauthenticated user enumeration via the user_id query parameter.
    if request.method == "GET":
        error, _ = decode_user_token(request.args, config.JWT_PRIVATE_KEY, check_if_admin=True)
        if error is not None: return error
    # (DELETE is for administrators only)
    if request.method in ["DELETE"]:
        error, _ = decode_user_token(rj, config.JWT_PRIVATE_KEY, check_if_admin=True)
        if error is not None: return error

    # Process the request
    if request.method == "GET":
        # Get all games, get a game by its ID, or get games by user/vision ID
        game_id = request.args.get("game_id")
        vision_id = request.args.get("vision_id")
        user_id = request.args.get("user_id")
        gn = game_id is None
        vn = vision_id is None
        un = user_id is None
        if gn and vn and un:
            return try_get_all_games()
        elif not gn and vn and un:
            return try_get_game_by_id(game_id)
        elif gn and not vn and un:
            return try_get_games_by_vision(vision_id)
        elif gn and vn and not un:
            return try_get_games_by_user(user_id)
        else:
            e = InvalidUsage("Too many query parameters.", status_code=400)
            return handle_invalid_usage(e)
    elif request.method == "POST":
        # Create a game
        error, user_json = decode_user_token(rj, config.JWT_PRIVATE_KEY, check_if_admin=False)
        if error is not None: return error
        user_id = user_json["user_id"]
        scenario_id = rj.get("scenario_id")
        return try_create_random_game(user_id, scenario_id=scenario_id)
    elif request.method == "PATCH":
        # Submit and update a game
        error, user_json = decode_user_token(rj, config.JWT_PRIVATE_KEY, check_if_admin=False)
        if error is not None: return error
        user_id = user_json["user_id"]
        game_id = rj.get("game_id")
        if game_id is None:
            e = InvalidUsage("Must have 'game_id'.", status_code=400)
            return handle_invalid_usage(e)
        feedback = rj.get("feedback")
        moods = rj.get("moods")
        if feedback is None and moods is None:
            e = InvalidUsage("Must have 'feedback' and/or 'moods'.", status_code=400)
            return handle_invalid_usage(e)
        else:
            return try_submit_game(game_id, user_id, feedback, moods)
    elif request.method == "DELETE":
        # Delete a game (admin only)
        game_id = rj.get("game_id")
        if game_id is None:
            e = InvalidUsage("Must have 'game_id'.", status_code=400)
            return handle_invalid_usage(e)
        else:
            return try_remove_game(game_id)
    else:
        # Wrong methods
        e = InvalidUsage("Method not allowed.", status_code=405)
        return handle_invalid_usage(e)


@try_wrap_response
def try_submit_game(game_id, user_id, feedback, moods, end_time=None):
    game = submit_game(game_id, user_id, feedback, moods, end_time=end_time)
    vision = get_vision_by_id(game.vision_id)
    game = game_schema.dump(game)
    game["vision"] = vision_mood_schema.dump(vision)
    return jsonify({"data": game})


@try_wrap_response
def try_get_game_by_id(game_id):
    data = get_game_by_id(game_id)
    return jsonify({"data": game_schema.dump(data)})


@try_wrap_response
def try_get_games_by_user(user_id):
    data = get_games_by_user(user_id)
    return jsonify({"data": games_schema.dump(data)})


@try_wrap_response
def try_get_games_by_vision(vision_id):
    data = get_games_by_vision(vision_id)
    return jsonify({"data": games_schema.dump(data)})


@try_wrap_response
def try_get_all_games():
    data = get_all_games()
    return jsonify({"data": games_schema.dump(data)})


@try_wrap_response
def try_create_random_game(user_id, scenario_id=None):
    game = create_random_game(user_id, scenario_id=scenario_id)
    if game is None:
        return make_response("", 204)
    else:
        vision = get_vision_by_id(game.vision_id)
        game = game_schema.dump(game)
        game["vision"] = vision_schema.dump(vision)
        return jsonify({"data": game})


@try_wrap_response
def try_remove_game(game_id):
    remove_game(game_id)
    return make_response("", 204)
