"""JSON responses when GCS credentials are missing or invalid."""

from flask import jsonify


def gcs_unavailable_response(exc: BaseException):
    if isinstance(exc, FileNotFoundError):
        return jsonify({"success": False, "message": str(exc)}), 503
    if isinstance(exc, RuntimeError) and "GOOGLE_APPLICATION_CREDENTIALS" in str(exc):
        return jsonify({"success": False, "message": str(exc)}), 503
    return None
