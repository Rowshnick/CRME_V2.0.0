#!/usr/bin/env python3

"""
CRME Repository Cleanup Tool
Version: 1.0

Purpose:
- Clean temporary files
- Organize backups
- Prepare repository for release
"""

import os
import shutil
from datetime import datetime


BASE = os.path.abspath(".")


ARCHIVE = os.path.join(
    BASE,
    "archive"
)

BACKUP_DIR = os.path.join(
    ARCHIVE,
    "backups"
)

REPORT = os.path.join(
    BASE,
    "cleanup_report.txt"
)


def log(message):

    print(message)

    with open(
        REPORT,
        "a",
        encoding="utf-8"
    ) as f:
        f.write(
            message + "\n"
        )


def ensure_dirs():

    folders = [
        BACKUP_DIR,
        os.path.join(
            BACKUP_DIR,
            "python"
        ),
        os.path.join(
            BACKUP_DIR,
            "releases"
        )
    ]

    for folder in folders:
        os.makedirs(
            folder,
            exist_ok=True
        )


def remove_path(path):

    if not os.path.exists(path):
        return

    if os.path.isdir(path):

        shutil.rmtree(path)

    else:

        os.remove(path)

    log(
        f"REMOVED: {path}"
    )


def move_backup(src, dst):

    if not os.path.exists(src):
        return

    target = os.path.join(
        dst,
        os.path.basename(src)
    )

    shutil.move(
        src,
        target
    )

    log(
        f"MOVED: {src} -> {target}"
    )


def clean_python_cache():

    for root, dirs, files in os.walk(BASE):

        for d in list(dirs):

            if d == "__pycache__":

                remove_path(
                    os.path.join(
                        root,
                        d
                    )
                )


def clean_verify_dirs():

    for root, dirs, files in os.walk(BASE):

        for d in list(dirs):

            if d.endswith(
                "_verify"
            ):

                remove_path(
                    os.path.join(
                        root,
                        d
                    )
                )


def clean_package_build():

    path = os.path.join(
        BASE,
        "exports",
        "package_build"
    )

    remove_path(path)


def organize_backups():

    core = os.path.join(
        BASE,
        "core"
    )

    for root, dirs, files in os.walk(core):

        for f in files:

            if (
                "backup" in f.lower()
                or
                "bak" in f.lower()
            ):

                move_backup(
                    os.path.join(
                        root,
                        f
                    ),
                    os.path.join(
                        BACKUP_DIR,
                        "python"
                    )
                )


def organize_zip_backups():

    for f in os.listdir(BASE):

        if (
            f.endswith(".zip")
            and
            "backup" in f.lower()
        ):

            move_backup(
                os.path.join(
                    BASE,
                    f
                ),
                os.path.join(
                    BACKUP_DIR,
                    "releases"
                )
            )


def main():

    with open(
        REPORT,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "CRME Cleanup Report\n"
        )

        f.write(
            str(datetime.now())
            +
            "\n\n"
        )


    ensure_dirs()

    log(
        "\n=== Cleaning Python Cache ==="
    )

    clean_python_cache()


    log(
        "\n=== Cleaning Verify Files ==="
    )

    clean_verify_dirs()


    log(
        "\n=== Cleaning Package Build ==="
    )

    clean_package_build()


    log(
        "\n=== Organizing Backups ==="
    )

    organize_backups()


    organize_zip_backups()


    log(
        "\n=== Cleanup Finished ==="
    )


if __name__ == "__main__":
    main()


