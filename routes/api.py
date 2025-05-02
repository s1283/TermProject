from flask import Blueprint, jsonify, request
from db import db

api_bp = Blueprint("api", __name__)