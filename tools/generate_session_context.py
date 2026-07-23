import os
from datetime import datetime

BASE = os.path.expanduser("~/CRME")

FILES = [
    "memory/session_rules/CRME_SESSION_RULES.md",
    "memory/latest.md",
    "memory/DECISION_LOG.md",
    "memory/ideas/IDEA-CRME-COMPANION-001.md"
]


OUTPUT = "CRME_SESSION_CONTEXT.md"


def main():

    with open(OUTPUT, "w", encoding="utf-8") as out:

        out.write("# CRME SESSION CONTEXT\n")
        out.write(
            f"Generated: {datetime.now()}\n\n"
        )

        for file in FILES:

            path = os.path.join(BASE, file)

            if os.path.exists(path):

                out.write(
                    "\n\n====================\n"
                )
                out.write(
                    file
                )
                out.write(
                    "\n====================\n\n"
                )

                with open(
                    path,
                    encoding="utf-8"
                ) as f:
                    out.write(f.read())


    print(
        "Session context generated:",
        OUTPUT
    )


if __name__ == "__main__":
    main()
