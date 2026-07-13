"""The controller for https://[PATH]/vision/"""

import traceback
from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from util.util import InvalidUsage
from util.util import handle_invalid_usage
from util.util import decode_user_token
from util.util import authorize_user_scoped_access
from util.util import try_wrap_response
from util.util import decode_jwt
from config.config import config
from models.model_operations.vision_operations import get_all_visions
from models.model_operations.vision_operations import get_visions_by_user
from models.model_operations.vision_operations import get_visions_by_scenario
from models.model_operations.vision_operations import get_vision_by_id
from models.model_operations.vision_operations import create_vision
from models.model_operations.vision_operations import remove_vision
from models.schema import visions_schema
from models.schema import vision_schema


bp = Blueprint("vision_controller", __name__)


@bp.route("/", methods=["GET", "POST", "PATCH", "DELETE"])
def vision():
    """
    The function for operating the vision table.

    Parameters
    ----------
    user_token : str
        The encoded user JWT, issued by the back-end.
        (required for POST, PATCH, and DELETE)
    scenario_id : int
        Scenario ID of the vision.
        (optional in the URL query parameters for GET)
        (required for POST)
    user_id : int
        User ID of the vision.
        (optional in the URL query parameters for GET)
    vision_id : int
        ID of the vision.
        (optional in the URL query parameters for GET)
        (required for PATCH and DELETE)
    mood_id : int
        Mood ID of the vision.
        (required for POST)
        (optional for PATCH)
    medias : list of dict
        List of media objects of the vision.
        See the docstring of create_vision in vision_operations.py file.
        (required for POST)
        (optional for PATCH)
    paginate : int
        Paginate the returned vision objects or not (0 means No, 1 means Yes).
        (optional for GET)
    pageNumber : int
        The page number for pagination.
        (optional for GET)
    pageSize : int
        The page size (number of items on each page) for pagination.
        (optional for GET)
    order : str
        The method for sorting the returned vision objects.
        See the docstring of get_all_visions in vision_operations.py file.
        (optional for GET)

    Returns
    -------
    Vision or list of Vision
        The retrieved vision object.
        (for GET with vision_id in the URL query parameters)
        (for POST and PATCH)
        Or a list of retrieved vision objects.
        (for GET with no URL query parameters)
        (for GET with scenario_id or user_id in the URL query parameters)
    """
    rj = request.json

    # Sanity and permission check
    # (POST, PATCH, and DELETE methods are for administrators only)
    if request.method in ["PATCH", "DELETE"]:
        error, _ = decode_user_token(rj, config.JWT_PRIVATE_KEY, check_if_admin=True)
        if error is not None: return error

    # Process the request
    if request.method == "GET":
        # Get all vision, or get visions by scenario/user ID, or get a vision by its ID
        scenario_id = request.args.get("scenario_id")
        user_id = request.args.get("user_id")
        vision_id = request.args.get("vision_id")
        paginate = bool(request.args.get("paginate", 1, type=int))
        page_number = request.args.get("pageNumber", 1, type=int)
        page_size = request.args.get("pageSize", 10, type=int)
        order = request.args.get("order", "desc", type=str)
        sn = scenario_id is None
        un = user_id is None
        vn = vision_id is None
        # Authorization: user-scoped reads (user_id present) require a valid
        # token belonging to that user or to an admin. This closes the user
        # enumeration / IDOR hole where anyone could read another user's visions
        # by guessing sequential user IDs. Public reads (all visions, by
        # scenario, or by vision ID) stay open.
        if not un:
            error, _ = authorize_user_scoped_access(
                request.args, config.JWT_PRIVATE_KEY, user_id)
            if error is not None: return error
        if sn and un and vn:
            return try_get_all_visions(paginate=paginate,
                    order=order, page_number=page_number, page_size=page_size)
        elif not sn and un and vn:
            return try_get_visions_by_scenario(scenario_id, paginate=paginate,
                    order=order, page_number=page_number, page_size=page_size)
        elif sn and not un and vn:
            return try_get_visions_by_user(user_id, paginate=paginate,
                    order=order, page_number=page_number, page_size=page_size)
        elif not sn and not un and vn:
            return try_get_visions_by_user(user_id, paginate=paginate,
                    order=order, page_number=page_number, page_size=page_size, scenario_id=scenario_id)
        elif sn and un and not vn:
            return try_get_vision_by_id(vision_id)
        else:
           e = InvalidUsage("Too many query parameters.", status_code=400)
           return handle_invalid_usage(e)
    elif request.method == "POST":
        # Create a vision
        mood_id = rj.get("mood_id")
        scenario_id = rj.get("scenario_id")
        medias = rj.get("medias")
        if mood_id is None or scenario_id is None or medias is None:
            e = InvalidUsage("Must have 'mood_id', 'scenario_id', and 'medias'.", status_code=400)
            return handle_invalid_usage(e)
        else:
            error, user_json = decode_user_token(rj, config.JWT_PRIVATE_KEY, check_if_admin=False)
            if error is not None: return error
            user_id = user_json["user_id"]
            return try_create_vision(mood_id, medias, user_id, scenario_id)
    elif request.method == "PATCH":
        # Update a vision (admin only)
        vision_id = rj.get("vision_id")
        if vision_id is None:
            e = InvalidUsage("Must have 'vision_id'.", status_code=400)
            return handle_invalid_usage(e)
        else:
            mood_id = rj.get("mood_id")
            medias = rj.get("medias")
            if mood_id is None and medias is None:
                e = InvalidUsage("Must have at least one field to update.", status_code=400)
                return handle_invalid_usage(e)
            else:
                return try_update_vision(vision_id, mood_id=mood_id, medias=medias)
    elif request.method == "DELETE":
        # Delete a vision (admin only)
        vision_id = rj.get("vision_id")
        if vision_id is None:
            e = InvalidUsage("Must have 'vision_id'.", status_code=400)
            return handle_invalid_usage(e)
        else:
            return try_remove_vision(vision_id)
    else:
        # Wrong methods
        e = InvalidUsage("Method not allowed.", status_code=405)
        return handle_invalid_usage(e)


@try_wrap_response
def try_get_all_visions(paginate=True, order="desc", page_number=1, page_size=30):
    data = get_all_visions(paginate=paginate,
            order=order, page_number=page_number, page_size=page_size)
    if paginate is True:
        total = data.total
        data = data.items
    else:
        total = len(data)
    return jsonify({"data": visions_schema.dump(data), "total": total})


@try_wrap_response
def try_get_visions_by_user(user_id, paginate=True, order="desc", page_number=1, page_size=30, scenario_id=None):
    data = get_visions_by_user(user_id, paginate=paginate,
            order=order, page_number=page_number, page_size=page_size, scenario_id=scenario_id)
    if paginate is True:
        total = data.total
        data = data.items
    else:
        total = len(data)
    return jsonify({"data": visions_schema.dump(data), "total": total})


@try_wrap_response
def try_get_visions_by_scenario(scenario_id, paginate=True, order="desc", page_number=1, page_size=30):
    data = get_visions_by_scenario(scenario_id, paginate=paginate,
            order=order, page_number=page_number, page_size=page_size)
    if paginate is True:
        total = data.total
        data = data.items
    else:
        total = len(data)
    return jsonify({"data": visions_schema.dump(data), "total": total})


@try_wrap_response
def try_get_vision_by_id(vision_id):
    data = get_vision_by_id(vision_id)
    return jsonify({"data": vision_schema.dump(data)})


@try_wrap_response
def try_create_vision(mood_id, medias, user_id, scenario_id):
    data = create_vision(mood_id, medias, user_id, scenario_id)
    return jsonify({"data": vision_schema.dump(data)})


@try_wrap_response
def try_update_vision(vision_id, mood_id=None, medias=None):
    data = update_vision(vision_id, mood_id=mood_id, medias=medias)
    return jsonify({"data": vision_schema.dump(data)})


@try_wrap_response
def try_remove_vision(vision_id):
    remove_vision(vision_id)
    return make_response("", 204)
