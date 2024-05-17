import os
import sys
import traceback

import requests


def main():
    if (url := os.getenv("HEALTH_CHECK_URL")) is None:
        raise ValueError("Environment variable not set: HEALTH_CHECK_URL")
    requests.get(f"{url}/health").raise_for_status()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
