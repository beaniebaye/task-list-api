from flask.wrappers import Response
from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, make_response, request, abort
from datetime import date

# Creates Blueprints

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

# Helper Functions

def valid_int(number, parameter_type):
    try:
        int(number)
    except:
        abort(make_response({"error": f"{parameter_type} must be an int"}, 400))

def get_task_from_id(task_id):
    valid_int(task_id, "task_id")
    return Task.query.get_or_404(task_id)

# Tasks Routes

@tasks_bp.route("", methods=["GET"])
def read_all_tasks():

    sort_query = request.args.get("sort")

    if sort_query == "asc":
        tasks = Task.query.order_by(Task.title).all()
    elif sort_query == "desc":
        tasks = Task.query.order_by(Task.title.desc()).all()
    else:
        tasks = Task.query.all()

    response_body = [task.to_dict() for task in tasks]

    return jsonify(response_body)

@tasks_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        response_body = {
            "details": "Invalid data"
        }
        return jsonify(response_body), 400

    new_task = Task(
        title=request_body["title"],
        description=request_body["description"],
        completed_at=request_body["completed_at"]
    )

    db.session.add(new_task)
    db.session.commit()

    response_body = {
        "task": new_task.to_dict()
    }

    return jsonify(response_body), 201

@tasks_bp.route("/<task_id>", methods=["GET"])
def read_one_task(task_id):
    task = get_task_from_id(task_id)

    response_body = {
        "task": task.to_dict()
    }

    return jsonify(response_body)

@tasks_bp.route("/<task_id>", methods=["PUT"])
def update_one_task(task_id):
    task = get_task_from_id(task_id)
    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body:
        response_body = "Invalid data"
        return jsonify(response_body), 400

    task.title = request_body["title"]
    task.description = request_body["description"]

    db.session.commit()

    response_body = {
        "task": task.to_dict()
    }

    return jsonify(response_body)

@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_one_task(task_id):
    task = get_task_from_id(task_id)
    db.session.delete(task)
    db.session.commit()

    response_body = {
        "details": f'Task {task_id} "{task.title}" successfully deleted'
    }

    return jsonify(response_body)

# Custom endpoints for Wave 03

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_task_as_complete(task_id):
    task = get_task_from_id(task_id)

    task.completed_at = date.today()

    db.session.commit()

    response_body = {
        "task": task.to_dict()
    }

    return jsonify(response_body)


@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_task_as_incomplete(task_id):
    task = get_task_from_id(task_id)

    task.completed_at = None

    db.session.commit()

    response_body = {
        "task": task.to_dict()
    }

    return jsonify(response_body)