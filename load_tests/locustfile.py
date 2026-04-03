"""
Locust load-test for the SENG 533 ProfileHub backend.

Endpoints exercised
───────────────────
  Read operations:
    POST /auth/login             (authenticates existing user)
    GET  /user/{email}           (fetches full profile)

  Write operations:
    POST /user/{email}/description     (JSON description upload)
    POST /user/{email}/profile-photo   (image upload, large mode only)

  Setup  (on_start):  POST /auth/signup   — creates the test user
  Teardown (on_stop): DELETE /user/{email} — optional cleanup

CLI flags
─────────
  --workload-type   read-heavy | write-heavy | mixed   (default: mixed)
  --data-size       small | large                       (default: large)
  --cleanup         off | on                            (default: off)
  --request-timeout seconds                             (default: 30)

Usage
─────
  # Headless (used by run_matrix.py):
  locust -f locustfile.py --host http://127.0.0.1:5000 \\
         --headless -u 50 -r 10 -t 300s \\
         --workload-type mixed --data-size large --cleanup on \\
         --csv results/mixed_large_50

  # Web UI:
  locust -f locustfile.py --host http://127.0.0.1:5000
"""

import random
from io import BytesIO
from urllib.parse import quote

from locust import HttpUser, between, events, task

from data_generators import (
    generate_description,
    generate_email,
    generate_password,
    generate_username,
    random_jpeg_bytes,
    random_png_bytes,
)

# ── Workload mix ratios ─────────────────────────────────────────────────────
# Value = probability that any given task iteration is a READ operation.
READ_RATIO = {
    "read-heavy":  0.80,
    "write-heavy": 0.20,
    "mixed":       0.50,
}


def _user_path_prefix(email: str) -> str:
    """Encode email for use in /user/<email>/... path segments (Flask matches decoded value)."""
    return f"/user/{quote(email, safe='')}"


# ── Custom CLI arguments ────────────────────────────────────────────────────
@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument(
        "--workload-type",
        type=str,
        default="mixed",
        choices=["read-heavy", "write-heavy", "mixed"],
        help="Read/write distribution.",
    )
    parser.add_argument(
        "--data-size",
        type=str,
        default="large",
        choices=["small", "large"],
        help="Payload size: small = JSON only, large = JSON + ~500 KB image.",
    )
    parser.add_argument(
        "--cleanup",
        type=str,
        default="off",
        choices=["off", "on"],
        help="Delete test users on stop (recommended for repeated runs).",
    )
    parser.add_argument(
        "--request-timeout",
        type=float,
        default=30.0,
        help="Per-request timeout in seconds.",
    )


# ── Locust user class ──────────────────────────────────────────────────────
class ProfileHubUser(HttpUser):
    """
    Simulates a single user interacting with the ProfileHub backend.

    Lifecycle
    ─────────
    on_start  → signs up a brand-new user (POST /auth/signup)
    @task     → randomly picks a read or write operation per the workload ratio
    on_stop   → optionally deletes the user (cleanup mode)
    """

    wait_time = between(0.5, 2.0)

    # ── Setup ───────────────────────────────────────────────────────────────
    def on_start(self):
        opts = self.environment.parsed_options

        # Generate unique identity for this simulated user
        self.email           = generate_email()
        self.username        = generate_username()
        self.password        = generate_password()
        self.description     = generate_description()

        # Pre-generate image bytes once (avoids regenerating per request)
        if opts.data_size == "large":
            self.image_bytes = random_png_bytes()          # ~500-700 KB
            self.image_name  = "profile_512x512.png"
            self.image_mime  = "image/png"
        else:
            self.image_bytes = random_jpeg_bytes()          # ~8-12 KB
            self.image_name  = "profile_64x64.jpg"
            self.image_mime  = "image/jpeg"

        # Store config
        self.workload_type   = opts.workload_type
        self.data_size       = opts.data_size
        self.cleanup_enabled = opts.cleanup == "on"
        self.timeout         = opts.request_timeout
        self.read_ratio      = READ_RATIO[self.workload_type]

        # Sign up — creates the user row in MySQL
        self.client.post(
            "/auth/signup",
            json={
                "email":    self.email,
                "username": self.username,
                "password": self.password,
            },
            name="POST /auth/signup [setup]",
            timeout=self.timeout,
        )

    # ── Read operations ─────────────────────────────────────────────────────
    def _do_login(self):
        """POST /auth/login — exercises bcrypt verify + MySQL lookup."""
        self.client.post(
            "/auth/login",
            json={
                "email":    self.email,
                "password": self.password,
            },
            name="POST /auth/login",
            timeout=self.timeout,
        )

    def _do_get_profile(self):
        """GET /user/{email} — fetches full profile row from MySQL."""
        self.client.get(
            _user_path_prefix(self.email),
            name="GET /user/[email]",
            timeout=self.timeout,
        )

    def _read(self):
        """Pick a random read operation."""
        if random.random() < 0.35:
            self._do_login()
        else:
            self._do_get_profile()

    # ── Write operations ────────────────────────────────────────────────────
    def _do_upload_description(self):
        """POST /user/{email}/description — uploads JSON description to GCS."""
        self.client.post(
            f"{_user_path_prefix(self.email)}/description",
            json={"description": self.description},
            name="POST /user/[email]/description",
            timeout=self.timeout,
        )

    def _do_upload_photo(self):
        """POST /user/{email}/profile-photo — uploads image to GCS."""
        file_obj = BytesIO(self.image_bytes)
        self.client.post(
            f"{_user_path_prefix(self.email)}/profile-photo",
            files={"file": (self.image_name, file_obj, self.image_mime)},
            name="POST /user/[email]/profile-photo",
            timeout=self.timeout,
        )

    def _write(self):
        """
        Pick a write operation.
        - small mode:  description only (no photo upload)
        - large mode:  70% photo upload, 30% description
        """
        if self.data_size == "small":
            self._do_upload_description()
        else:
            if random.random() < 0.70:
                self._do_upload_photo()
            else:
                self._do_upload_description()

    # ── Main task ───────────────────────────────────────────────────────────
    @task
    def do_operation(self):
        """Single task iteration: read or write based on workload ratio."""
        if random.random() < self.read_ratio:
            self._read()
        else:
            self._write()

    # ── Teardown ────────────────────────────────────────────────────────────
    def on_stop(self):
        if not self.cleanup_enabled:
            return
        self.client.delete(
            _user_path_prefix(self.email),
            name="DELETE /user/[email] [cleanup]",
            timeout=self.timeout,
        )
