
import urllib.request
import urllib.error
import getpass
import json
import time
from datetime import datetime

USERNAME = "Reak"
INTERVAL = 16

BASE = "https://api.minecraftservices.com/minecraft/profile"

TOKEN = getpass.getpass("Minecraft bearer token: ")

if not TOKEN:
    raise SystemExit("Missing token.")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json",
    "User-Agent": "ReakSniper/1.0"
}


def request(method, url):
    req = urllib.request.Request(
        url,
        headers=HEADERS,
        method=method
    )

    with urllib.request.urlopen(req, timeout=20) as response:
        body = response.read().decode("utf-8")
        return response.status, body


def log(message):
    print(
        f"[{datetime.now().strftime('%H:%M:%S')}] {message}",
        flush=True
    )


def claim():
    log("AVAILABLE! ATTEMPTING CLAIM NOW!")

    try:
        status, body = request(
            "PUT",
            f"{BASE}/name/{USERNAME}"
        )

        log(f"HTTP {status}")

        if body:
            print(json.dumps(json.loads(body), indent=2))

        log("CLAIM REQUEST SUCCESSFUL.")
        return True

    except urllib.error.HTTPError as e:
        log(f"CLAIM FAILED: HTTP {e.code}")
        log(e.read().decode("utf-8", errors="replace"))
        return False

    except Exception as e:
        log(f"CLAIM ERROR: {e}")
        return False


def main():
    log(f"Starting monitor for {USERNAME}")
    log(f"Interval: {INTERVAL} seconds")

    backoff = 60

    while True:
        try:
            status, body = request(
                "GET",
                f"{BASE}/name/{USERNAME}/available"
            )

            result = json.loads(body).get("status", "UNKNOWN")
            log(f"Availability: {result}")

            backoff = 60

            if result == "AVAILABLE":
                claim()
                break

            if result == "NOT_ALLOWED":
                log("Username is not allowed.")
                break

            if result not in ("DUPLICATE",):
                log("Unexpected response. Stopping.")
                break

        except urllib.error.HTTPError as e:
            log(f"HTTP ERROR: {e.code}")

            if e.code == 401:
                log("Token invalid or expired.")
                break

            if e.code == 429:
                log(f"Rate limited. Waiting {backoff}s.")
                time.sleep(backoff)
                backoff = min(backoff * 2, 900)
                continue

            if e.code == 403:
                log("Access forbidden.")
                break

        except Exception as e:
            log(f"Connection error: {e}")

        time.sleep(INTERVAL)

    log("MONITOR FINISHED.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Stopped by user.")
