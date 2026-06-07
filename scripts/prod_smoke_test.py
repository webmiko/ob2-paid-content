#!/usr/bin/env python3
"""Smoke-тест production Creavity."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

BASE = "http://158.160.242.143"
API = f"{BASE}/api"
DEMO = ("79000001001", "DemoPass123")

passed: list[str] = []
failed: list[str] = []


def ok(name: str) -> None:
    passed.append(name)
    print(f"✓ {name}")


def bad(name: str, detail: str = "") -> None:
    failed.append(name)
    line = f"✗ {name}"
    if detail:
        line += f" — {detail[:180]}"
    print(line)


def req(method: str, url: str, *, token: str | None = None, body: dict | None = None):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=25) as resp:
            raw = resp.read()
            payload = json.loads(raw.decode()) if raw else None
            return resp.status, payload
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            payload = json.loads(raw.decode()) if raw else {}
        except json.JSONDecodeError:
            payload = raw.decode()[:180]
        return exc.code, payload


def get(url: str) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            return resp.status, resp.read(500).decode(errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(200).decode(errors="replace")


def main() -> int:
    print(f"=== Production smoke: {BASE} ===\n")

    for name, url, needle in (
        ("health", f"{API}/health/", '"status"'),
        ("robots", f"{BASE}/robots.txt", "Sitemap"),
        ("sitemap", f"{BASE}/sitemap.xml", "urlset"),
        ("manifest", f"{BASE}/manifest.webmanifest", "Creavity"),
        ("sw.js", f"{BASE}/sw.js", "define"),
        ("admin", f"{BASE}/admin/", "admin"),
    ):
        code, body = get(url)
        ok(name) if code == 200 and needle in body else bad(name, str(code))

    for route in ("/", "/login", "/profile", "/authors", "/explore"):
        code, _ = get(f"{BASE}{route}")
        ok(f"SPA {route}") if code == 200 else bad(f"SPA {route}", str(code))

    code, posts = req("GET", f"{API}/posts/")
    count = posts.get("count", 0) if isinstance(posts, dict) else 0
    ok(f"posts ({count})") if code == 200 and count else bad("posts", str(posts))

    code, tokens = req("POST", f"{API}/token/", body={"phone": DEMO[0], "password": DEMO[1]})
    access = tokens.get("access") if isinstance(tokens, dict) else None
    if not access:
        bad("login", str(tokens))
        print(f"\nPassed {len(passed)}, failed {len(failed)}")
        return 1
    ok("login demo")

    code, me = req("GET", f"{API}/users/me/", token=access)
    ok("profile") if code == 200 else bad("profile", str(me))

    code, pay = req("POST", f"{API}/payments/create/", token=access, body={})
    if code in (200, 201) and isinstance(pay, dict) and "checkout.stripe.com" in pay.get("payment_url", ""):
        ok("Stripe checkout")
    else:
        bad("Stripe checkout", str(pay))

    paid_id = next((p["id"] for p in posts.get("results", []) if p.get("is_paid")), None)
    if paid_id:
        code, anon = req("GET", f"{API}/posts/{paid_id}/")
        ok("paid hides video (anon)") if code == 200 and isinstance(anon, dict) and not anon.get("video_url") else bad(
            "paid anon",
            str(anon),
        )

    code, reg = req(
        "POST",
        f"{API}/users/register/",
        body={"phone": f"7900{__import__('time').time_ns() % 10_000_000:07d}", "password": "TestPass123!", "display_name": "Smoke"},
    )
    ok("register") if code in (200, 201) else bad("register", str(reg))

    print(f"\nPassed {len(passed)}, failed {len(failed)}")
    if failed:
        print("Failed:", ", ".join(failed))
        return 1
    print("RESULT: ALL PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
