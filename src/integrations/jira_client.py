"""Jira API client for issue ingestion and metric extraction."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib import parse, request
from urllib.error import HTTPError, URLError

from src.integrations.oauth_handler import JiraOAuthHandler


class JiraConnectionError(Exception):
    """Raised when Jira connectivity fails."""


class InvalidJQLError(Exception):
    """Raised when a provided JQL query is invalid."""


class RateLimitError(Exception):
    """Raised when Jira API rate limits are exceeded."""


class JiraHTTPStatusError(JiraConnectionError):
    """Raised when Jira responds with an HTTP status code."""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass
class JiraCredentials:
    base_url: str
    user_email: str
    api_token: str
    project_key: str
    access_token: str = ""
    cloud_id: str = ""
    refresh_token: str = ""
    token_expires_at: float = 0.0


class JiraAPIClient:
    """Lightweight Jira REST client for project issue ingestion."""

    def __init__(
        self,
        base_url: str,
        user_email: str = "",
        api_token: str = "",
        project_key: str = "",
        access_token: str = "",
        cloud_id: str = "",
        refresh_token: str = "",
        token_expires_at: float = 0.0,
        oauth_handler: Optional[JiraOAuthHandler] = None,
        timeout_seconds: int = 20,
    ) -> None:
        has_basic = bool(user_email and api_token)
        has_oauth = bool(access_token)
        if not base_url or not project_key or (not has_basic and not has_oauth):
            raise JiraConnectionError("Jira credentials are incomplete")

        self.credentials = JiraCredentials(
            base_url=base_url.rstrip("/"),
            user_email=user_email,
            api_token=api_token,
            project_key=project_key,
            access_token=access_token,
            cloud_id=cloud_id,
            refresh_token=refresh_token,
            token_expires_at=float(token_expires_at or 0.0),
        )
        self.timeout_seconds = timeout_seconds
        self.oauth_handler = oauth_handler
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("jira.integration")
        if logger.handlers:
            return logger

        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(log_dir / "jira_integration.log")
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
        return logger

    def _auth_header(self) -> Dict[str, str]:
        if self.credentials.access_token:
            self._ensure_valid_oauth_token()
            return {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }

        token_bytes = (
            f"{self.credentials.user_email}:{self.credentials.api_token}".encode(
                "utf-8"
            )
        )
        import base64

        auth_token = base64.b64encode(token_bytes).decode("ascii")
        return {
            "Authorization": f"Basic {auth_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _ensure_valid_oauth_token(self) -> None:
        if not self.credentials.access_token:
            return

        if not self.credentials.token_expires_at:
            return

        if not JiraOAuthHandler.is_token_expired(self.credentials.token_expires_at):
            return

        if not self.oauth_handler or not self.credentials.refresh_token:
            raise JiraConnectionError(
                "Jira OAuth token expired and refresh configuration is missing"
            )

        refreshed = self.oauth_handler.refresh_access_token(
            self.credentials.refresh_token
        )
        self.update_oauth_credentials(
            access_token=refreshed.get("access_token", ""),
            refresh_token=refreshed.get("refresh_token")
            or self.credentials.refresh_token,
            token_expires_at=float(refreshed.get("expires_at", 0.0)),
        )

    def _request_json(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if self.credentials.access_token and self.credentials.cloud_id:
            url = f"https://api.atlassian.com/ex/jira/{self.credentials.cloud_id}{endpoint}"
        else:
            url = f"{self.credentials.base_url}{endpoint}"
        if params:
            url = f"{url}?{parse.urlencode(params)}"

        req = request.Request(url, headers=self._auth_header(), method="GET")
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore") if exc.fp else ""
            if exc.code == 400 and "jql" in body.lower():
                raise InvalidJQLError(body or "Invalid JQL query") from exc
            if exc.code == 429:
                raise RateLimitError("Jira API rate limit exceeded") from exc
            raise JiraHTTPStatusError(
                exc.code,
                f"Jira request failed: HTTP {exc.code}",
            ) from exc
        except URLError as exc:
            raise JiraConnectionError(f"Jira network error: {exc}") from exc

    def handle_rate_limiting(
        self, retry_count: int = 3, backoff_seconds: float = 1.5
    ) -> None:
        """Sleep with exponential backoff used after rate-limit responses."""
        for attempt in range(retry_count):
            sleep_for = backoff_seconds * (2**attempt)
            self.logger.warning("Rate limited by Jira; retrying in %.1fs", sleep_for)
            time.sleep(sleep_for)

    def fetch_issues(
        self, jql_query: str, max_results: int = 1000
    ) -> List[Dict[str, Any]]:
        """Fetch Jira issues using JQL with pagination."""
        issues: List[Dict[str, Any]] = []
        start_at = 0
        page_size = 100

        while start_at < max_results:
            params = {
                "jql": jql_query,
                "startAt": start_at,
                "maxResults": min(page_size, max_results - start_at),
                "fields": "summary,description,priority,issuetype,customfield_10016,timeoriginalestimate,timespent,created,updated,status",
            }
            try:
                payload = self._request_json("/rest/api/3/search", params)
            except JiraHTTPStatusError as exc:
                if exc.status_code != 410:
                    raise
                self.logger.info(
                    "Jira /rest/api/3/search returned HTTP 410; retrying with /rest/api/3/search/jql"
                )
                payload = self._request_json("/rest/api/3/search/jql", params)
            page = payload.get("issues", [])
            if not page:
                break

            issues.extend(page)
            start_at += len(page)
            if len(page) < params["maxResults"]:
                break

        self.logger.info("Fetched %d Jira issues", len(issues))
        return issues

    def default_jql(self) -> str:
        """Return default project-scoped JQL for active issues."""
        return (
            f"project = {self.credentials.project_key} "
            "AND statusCategory != Done ORDER BY updated DESC"
        )

    def sync_issues(
        self,
        jql_query: Optional[str] = None,
        max_results: int = 250,
    ) -> List[Dict[str, Any]]:
        """Fetch Jira issues and convert to model-ready metric rows."""
        query = (jql_query or "").strip() or self.default_jql()
        issues = self.fetch_issues(query, max_results=max_results)
        return self.issues_to_metrics(issues)

    def issues_to_metrics(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert raw Jira payload list into model-ready metric rows."""
        rows: List[Dict[str, Any]] = []
        for issue in issues:
            row = self.extract_metrics(issue)
            row["Issue_key"] = issue.get("key", "")
            row["Issue_ID"] = issue.get("id", "")
            rows.append(row)
        return rows

    def update_oauth_credentials(
        self,
        access_token: str,
        refresh_token: Optional[str] = None,
        token_expires_at: float = 0.0,
        cloud_id: Optional[str] = None,
    ) -> None:
        """Update OAuth credentials after code exchange or refresh."""
        self.credentials.access_token = access_token
        if refresh_token is not None:
            self.credentials.refresh_token = refresh_token
        if token_expires_at:
            self.credentials.token_expires_at = float(token_expires_at)
        if cloud_id is not None:
            self.credentials.cloud_id = cloud_id

    def fetch_issue_by_key(self, issue_key: str) -> Dict[str, Any]:
        """Fetch a single issue by Jira key."""
        return self._request_json(f"/rest/api/3/issue/{issue_key}")

    def subscribe_to_webhooks(self, callback_url: str) -> Dict[str, str]:
        """Return webhook registration guidance payload for manual setup."""
        payload = {
            "status": "manual_required",
            "message": "Create webhook in Jira admin UI pointing to callback_url",
            "callback_url": callback_url,
        }
        self.logger.info("Webhook subscription requires manual Jira admin action")
        return payload

    def extract_metrics(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Map Jira issue fields to model-ready metrics used by dashboard engines."""
        fields = issue.get("fields", {})
        summary = fields.get("summary") or ""
        description = fields.get("description") or ""

        story_points = fields.get("customfield_10016")
        story_points = float(story_points) if story_points is not None else 3.0

        estimated_seconds = fields.get("timeoriginalestimate") or 0
        spent_seconds = fields.get("timespent") or 0
        estimated_days = max(1.0, round(float(estimated_seconds) / 28800.0, 2))
        actual_days = max(1.0, round(float(spent_seconds) / 28800.0, 2))

        budget_allocated = float(max(500.0, story_points * 250.0))
        cost_consumed = float(max(400.0, actual_days * 220.0 + story_points * 40.0))

        priority = (fields.get("priority") or {}).get("name", "Medium")
        issue_type = (fields.get("issuetype") or {}).get("name", "Task")

        return {
            "Priority": priority,
            "Issue_Type": issue_type,
            "Assignee_Seniority": "Senior",
            "Story_Points": story_points,
            "Estimated_Days": estimated_days,
            "Actual_Days": actual_days,
            "Budget_Allocated": budget_allocated,
            "Cost_Consumed": cost_consumed,
            "Summary": summary,
            "Description": description,
            "Risk_Level": "Medium",
        }
