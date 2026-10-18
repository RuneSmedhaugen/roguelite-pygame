"""Asynchronous feedback submission to the game's hosted feedback API."""

import json
import os
import queue
import threading
import urllib.error
import urllib.request


DEFAULT_FEEDBACK_URL = "https://br-noisy-unit-b84wai0k-feedback.compute.c-14.us-east-1.aws.neon.tech/"


class FeedbackClient:
    def __init__(self):
        self.api_url = os.environ.get(
            "SMALL_PUNCH_PUPPIES_FEEDBACK_URL",
            os.environ.get("TROLLGAME_FEEDBACK_URL", DEFAULT_FEEDBACK_URL),
        ).strip()
        self.results = queue.Queue()

    def submit(self, kind, message):
        if not self.api_url:
            self.results.put((False, "Feedback sending isn't configured yet."))
            return

        payload = json.dumps({"type": kind, "message": message}).encode("utf-8")

        def send():
            request = urllib.request.Request(
                self.api_url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=12) as response:
                    if 200 <= response.status < 300:
                        self.results.put((True, "Sent! Thanks for helping improve the game."))
                    else:
                        self.results.put((False, f"Feedback service error (HTTP {response.status}). Please try again."))
            except urllib.error.HTTPError as error:
                self.results.put((False, f"Feedback service error (HTTP {error.code}). Please try again."))
            except (urllib.error.URLError, TimeoutError, OSError):
                self.results.put((False, "Could not send. Check your connection and try again."))

        threading.Thread(target=send, daemon=True).start()

    def take_result(self):
        try:
            return self.results.get_nowait()
        except queue.Empty:
            return None
