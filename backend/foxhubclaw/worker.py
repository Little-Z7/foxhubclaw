from __future__ import annotations

from foxhubclaw.db import init_db
from foxhubclaw.scheduler import process_due_jobs


def main() -> None:
    init_db()
    count = process_due_jobs()
    print(f"FoxHubClaw worker finished {count} due job(s)")


if __name__ == "__main__":
    main()
