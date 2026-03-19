import random
from io import BytesIO

from locust import HttpUser, between, events, task

from data_generators import (
    generate_email,
    generate_password,
    generate_username,
    random_png_bytes,
)

READ_RATIO_BY_WORKLOAD = {
    "read-heavy": 0.80,
    "write-heavy": 0.20,
    "mixed": 0.50,
}


@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument(
        "--workload-type",
        type=str,
        default="mixed",
        choices=["read-heavy", "write-heavy", "mixed"],
        help="Workload mix for request distribution.",
    )
    parser.add_argument(
        "--data-size",
        type=str,
        default="large",
        choices=["small", "large"],
        help="Write payload size mode.",
    )
    parser.add_argument(
        "--cleanup",
        type=str,
        default="off",
        choices=["off", "on"],
        help="Whether generated users should be deleted in on_stop.",
    )
    parser.add_argument(
        "--request-timeout",
        type=float,
        default=5.0,
        help="Per-request timeout in seconds.",
    )


class UserEndpointLoadTest(HttpUser):
    wait_time = between(0.5, 2.0)

    def on_start(self):
        options = self.environment.parsed_options
        self.email = generate_email()
        self.username = generate_username()
        self.password = generate_password()
        self.profile_png = random_png_bytes()
        self.description_text = f"{self.username}'s description {generate_username(40)}"
        self.workload_type = options.workload_type
        self.data_size = options.data_size
        self.cleanup_enabled = options.cleanup == "on"
        self.request_timeout = options.request_timeout
        self.read_ratio = READ_RATIO_BY_WORKLOAD[self.workload_type]

        signup_payload = {
            "email": self.email,
            "username": self.username,
            "password": self.password,
        }

        self.client.post(
            "/auth/signup",
            json=signup_payload,
            name="/auth/signup",
            timeout=self.request_timeout,
        )

    def _read_user(self):
        self.client.get(
            f"/user/{self.email}",
            name="/user/[email]",
            timeout=self.request_timeout,
        )

    def _write_user_data(self):
        if self.data_size == "small":
            payload = {"description": self.description_text}
            self.client.post(
                f"/user/{self.email}/description",
                json=payload,
                name="/user/[email]/description",
                timeout=self.request_timeout,
            )
            return

        file_obj = BytesIO(self.profile_png)
        files = {
            "file": ("random_512x512.png", file_obj, "image/png"),
        }
        self.client.post(
            f"/user/{self.email}/profile-photo",
            files=files,
            name="/user/[email]/profile-photo",
            timeout=self.request_timeout,
        )

    @task
    def mixed_operation(self):
        if random.random() < self.read_ratio:
            self._read_user()
            return
        self._write_user_data()

    def on_stop(self):
        if not self.cleanup_enabled:
            return

        self.client.delete(
            f"/user/{self.email}",
            name="/user/[email] DELETE",
            timeout=self.request_timeout,
        )
