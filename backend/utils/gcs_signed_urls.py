"""Time-limited signed HTTPS URLs so the browser can load private GCS objects (<img>, fetch)."""

from __future__ import annotations

import logging
import urllib.parse
from datetime import timedelta

from cloudStorage.GCP import set_gcs_connection
from utils.config import BaseConfig as config

BUCKET = config.GCS_BUCKET


def object_name_from_stored_gcs_url(stored_url: str | None) -> str | None:
    """
    Extract the object path from our stored URL
    https://storage.googleapis.com/<bucket>/<object>
    Handles query strings, fragments, and percent-encoding (e.g. %40 in emails).
    """
    if not stored_url or not BUCKET:
        return None
    prefix = f"https://storage.googleapis.com/{BUCKET}/"
    if not stored_url.startswith(prefix):
        return None
    rest = stored_url[len(prefix) :].split("?")[0].split("#")[0]
    name = urllib.parse.unquote(rest)
    return name if name else None


def sign_gcs_https_url(url: str | None) -> str | None:
    """
    Turn a stored public-style URL into a v4 signed GET URL (1 hour).
    If signing fails or the URL is not our bucket prefix, returns the original string.
    """
    if not url or not BUCKET:
        return url
    prefix = f"https://storage.googleapis.com/{BUCKET}/"
    if not url.startswith(prefix):
        return url
    path = url[len(prefix) :].split("?")[0]
    object_name = urllib.parse.unquote(path)
    try:
        bucket = set_gcs_connection()
        blob = bucket.blob(object_name)
        return blob.generate_signed_url(
            version="v4",
            expiration=timedelta(hours=1),
            method="GET",
        )
    except Exception as e:
        logging.warning("Could not sign GCS URL; returning original: %s", e)
        return url


def sign_user_dict_for_client(user: dict | None) -> dict | None:
    if not user:
        return None
    out = dict(user)
    if out.get("pictureURL"):
        out["pictureURL"] = sign_gcs_https_url(out["pictureURL"])
    if out.get("userDescriptionURL"):
        out["userDescriptionURL"] = sign_gcs_https_url(out["userDescriptionURL"])
    return out
