from datetime import UTC, datetime, timedelta

import jwt

from packages.config.settings import get_settings


class GitHubAppAuth:
    """Handles authentication for the RepoPilot GitHub App."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def _load_private_key(self) -> str:
        with open(
            self.settings.github_private_key_path,
            "r",
            encoding="utf-8",
        ) as file:
            return file.read()

    def create_app_jwt(self) -> str:
        """Create a short-lived JWT for GitHub App authentication."""

        now = datetime.now(UTC)

        payload = {
            "iat": int(now.timestamp()) - 60,
            "exp": int((now + timedelta(minutes=9)).timestamp()),
            "iss": self.settings.github_app_id,
        }

        private_key = self._load_private_key()

        return jwt.encode(
            payload,
            private_key,
            algorithm="RS256",
        )
