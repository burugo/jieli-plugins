#!/usr/bin/env python3
"""Find Jieli threads with compact agent-friendly output."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

import jieli_config


THREADS_TIMEOUT_SECONDS = 20
DEFAULT_BASE_URL = jieli_config.DEFAULT_BASE_URL


def required_env(*names: str) -> str:
    if names and names[0] == "JIELI_API_KEY":
        value = jieli_config.get_api_key()
        if value:
            return value
    raise KeyError(names[0])


def optional_env(*names: str) -> str:
    if names and names[0] == "JIELI_BASE_URL":
        return jieli_config.get_base_url()
    return ""


def fetch_threads(
    query: str,
    base_url: str,
    api_key: str,
    provider: str | None = None,
    repo: str | None = None,
    label: str | None = None,
    page_size: int = 10,
    page: int | None = None,
    sort: str = "updated",
) -> dict[str, Any]:
    params: dict[str, str] = {
        "search": query,
        "page_size": str(page_size),
        "sort": sort,
    }
    if provider:
        params["provider"] = provider
    if repo:
        params["repo"] = repo
    if label:
        params["label"] = label
    if page is not None:
        params["page"] = str(page)

    url = f"{base_url.rstrip('/')}/plugin/threads?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {api_key}"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=THREADS_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def _thread_list(payload: dict[str, Any]) -> list[dict[str, Any]]:
    data = payload.get("data")
    if isinstance(data, dict) and isinstance(data.get("threads"), list):
        return [thread for thread in data["threads"] if isinstance(thread, dict)]
    if isinstance(payload.get("threads"), list):
        return [thread for thread in payload["threads"] if isinstance(thread, dict)]
    return []


def _first_text(thread: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = thread.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def format_threads_markdown(payload: dict[str, Any], base_url: str) -> str:
    threads = _thread_list(payload)
    if not threads:
        return "No matching Jieli threads found.\n"

    lines: list[str] = []
    for index, thread in enumerate(threads, start=1):
        thread_id = _first_text(thread, "provider_thread_id", "id", "thread_id")
        title = _first_text(thread, "title") or "Untitled thread"
        provider = _first_text(thread, "provider") or "unknown"
        repo = _first_text(thread, "repo")
        branch = _first_text(thread, "branch")
        updated = _first_text(thread, "updated_at", "updated", "updatedAt")
        preview = _first_text(thread, "preview", "summary", "snippet")
        message_count = thread.get("message_count", thread.get("messages_count", thread.get("messageCount", "")))
        repo_branch = repo
        if branch:
            repo_branch = f"{repo_branch}@{branch}" if repo_branch else branch
        read_url = f"{base_url.rstrip('/')}/threads/{urllib.parse.quote(thread_id, safe='')}" if thread_id else ""

        lines.append(f"{index}. {title}")
        lines.append(f"   provider: {provider}")
        if thread_id:
            lines.append(f"   thread_id: {thread_id}")
        if repo_branch:
            lines.append(f"   repo: {repo_branch}")
        if updated:
            lines.append(f"   updated: {updated}")
        if message_count != "":
            lines.append(f"   messages: {message_count}")
        if preview:
            lines.append(f"   preview: {preview}")
        if read_url:
            lines.append(f"   read_url: {read_url}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Find Jieli threads.")
    parser.add_argument("query", help="Search keywords, repo/file/topic, or other clue.")
    parser.add_argument("--provider", help="Filter to a provider only when explicitly requested.")
    parser.add_argument("--repo", help="Filter by repo.")
    parser.add_argument("--label", help="Filter by label.")
    parser.add_argument("--page-size", type=int, default=10)
    parser.add_argument("--page", type=int)
    parser.add_argument("--sort", default="updated")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args()

    try:
        base_url = optional_env("JIELI_BASE_URL") or DEFAULT_BASE_URL
        api_key = required_env("JIELI_API_KEY")
        payload = fetch_threads(
            args.query,
            base_url,
            api_key,
            provider=args.provider,
            repo=args.repo,
            label=args.label,
            page_size=args.page_size,
            page=args.page,
            sort=args.sort,
        )
        if args.format == "json":
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(format_threads_markdown(payload, base_url), end="")
        return 0
    except (KeyError, ValueError, urllib.error.URLError, json.JSONDecodeError) as error:
        print(f"find_threads failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
