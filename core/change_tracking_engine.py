import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from copy import deepcopy


class ChangeTrackingEngine:
    """
    CRME Change Tracking Engine
    Version 1.2.2

    Persistent, auditable project change history.

    Tracks:
        - added items
        - removed items
        - modified items
        - unchanged items inside changed collections
        - fundamental changes
        - structural changes
        - decisions
        - session provenance
        - before/after state
        - fingerprints
        - project evolution
        - file-level changes
        - item-level collection changes
        - state reconstruction
        - machine-readable logs
        - Markdown history

    Core principle
    --------------
    Every important state transition should be represented as:

        BEFORE STATE
            +
        AFTER STATE
            +
        CHANGE DETECTION
            +
        ITEM-LEVEL ANALYSIS
            +
        SESSION PROVENANCE
            +
        DECISION CONTEXT
            =
        REPRODUCIBLE PROJECT HISTORY

    The engine does not mutate the canonical source of truth
    unless explicitly instructed by the caller.

    It is therefore designed as a tracking and audit layer.
    """

    VERSION = "1.2.2"

    CHANGE_TYPES = {
        "ADDED",
        "REMOVED",
        "MODIFIED",
        "FUNDAMENTAL",
        "STRUCTURAL",
        "UNCHANGED",
    }

    FUNDAMENTAL_CHANGE_KEYS = {
        "architecture",
        "system_architecture",
        "core_architecture",
        "research_question",
        "research_problem",
        "methodology",
        "evaluation_protocol",
        "evaluation_design",
        "paper_claims",
        "project_goal",
        "current_phase",
        "status",
    }

    STRUCTURAL_CHANGE_KEYS = {
        "modules",
        "components",
        "files",
        "dependencies",
        "milestones",
        "pipelines",
        "datasets",
        "evaluation",
        "experiments",
    }

    def __init__(
        self,
        base_path=".",
        project_id="CRME-001",
    ):
        self.base_path = Path(base_path)
        self.project_id = project_id

        self.memory_dir = self.base_path / "memory"
        self.change_dir = self.memory_dir / "changes"

        self.change_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.change_log_path = (
            self.change_dir / "change_log.json"
        )

        self.change_index_path = (
            self.change_dir / "change_index.json"
        )

        self.latest_change_path = (
            self.change_dir / "latest_change.json"
        )

        self.change_history_markdown_path = (
            self.change_dir / "CHANGE_HISTORY.md"
        )

        self._ensure_storage()

    # =========================================================
    # TIME
    # =========================================================

    def _now(self):
        return datetime.now(
            timezone.utc
        ).isoformat()

    # =========================================================
    # STORAGE
    # =========================================================

    def _default_change_log(self):
        return {
            "project_id": self.project_id,
            "engine_version": self.VERSION,
            "created_at": self._now(),
            "changes": [],
        }

    def _default_change_index(self):
        return {
            "project_id": self.project_id,
            "engine_version": self.VERSION,
            "total_changes": 0,
            "total_events": 0,
            "sessions": {},
            "change_types": {},
            "files": {},
            "paths": {},
            "fundamental_changes": 0,
            "structural_changes": 0,
            "item_added": 0,
            "item_removed": 0,
            "item_modified": 0,
            "item_unchanged": 0,
        }

    def _ensure_storage(self):

        if not self.change_log_path.exists():

            self._save_json(
                self.change_log_path,
                self._default_change_log(),
            )

        if not self.change_index_path.exists():

            self._save_json(
                self.change_index_path,
                self._default_change_index(),
            )

    def _load_json(
        self,
        path,
    ):

        path = Path(path)

        if not path.exists():
            return None

        try:

            with open(
                path,
                "r",
                encoding="utf-8",
            ) as file:

                return json.load(file)

        except (
            json.JSONDecodeError,
            OSError,
            TypeError,
        ):

            return None

    def _save_json(
        self,
        path,
        data,
    ):

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp_path = path.with_suffix(
            path.suffix + ".tmp"
        )

        with open(
            temp_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )

        temp_path.replace(path)

    # =========================================================
    # NORMALIZATION / FINGERPRINT
    # =========================================================

    def _normalize(
        self,
        value,
    ):

        if isinstance(
            value,
            dict,
        ):

            return {
                str(key): self._normalize(
                    value[key]
                )
                for key in sorted(
                    value.keys(),
                    key=lambda item: str(item),
                )
            }

        if isinstance(
            value,
            list,
        ):

            return [
                self._normalize(item)
                for item in value
            ]

        if isinstance(
            value,
            tuple,
        ):

            return [
                self._normalize(item)
                for item in value
            ]

        if isinstance(
            value,
            set,
        ):

            return sorted(
                [
                    self._normalize(item)
                    for item in value
                ],
                key=lambda item: str(item),
            )

        return value

    def _canonical_json(
        self,
        value,
    ):

        return json.dumps(
            self._normalize(value),
            sort_keys=True,
            ensure_ascii=False,
            separators=(
                ",",
                ":",
            ),
        )

    def _fingerprint(
        self,
        value,
    ):

        raw = self._canonical_json(
            value
        )

        return hashlib.sha256(
            raw.encode(
                "utf-8"
            )
        ).hexdigest()

    # =========================================================
    # CLASSIFICATION
    # =========================================================

    def _is_fundamental_key(
        self,
        key,
    ):

        return (
            str(key).lower()
            in {
                item.lower()
                for item in
                self.FUNDAMENTAL_CHANGE_KEYS
            }
        )

    def _is_structural_key(
        self,
        key,
    ):

        return (
            str(key).lower()
            in {
                item.lower()
                for item in
                self.STRUCTURAL_CHANGE_KEYS
            }
        )

    def _classify_change(
        self,
        key,
        before,
        after,
        before_exists=True,
        after_exists=True,
    ):

        if (
            not before_exists
            and after_exists
        ):

            return "ADDED"

        if (
            before_exists
            and not after_exists
        ):

            return "REMOVED"

        if (
            before is None
            and after is not None
        ):

            return "ADDED"

        if (
            before is not None
            and after is None
        ):

            return "REMOVED"

        if before == after:

            return "UNCHANGED"

        if self._is_fundamental_key(
            key
        ):

            return "FUNDAMENTAL"

        if self._is_structural_key(
            key
        ):

            return "STRUCTURAL"

        return "MODIFIED"

    # =========================================================
    # ITEM-LEVEL CHANGE DETECTION
    # =========================================================

    def _diff_list_items(
        self,
        before,
        after,
    ):

        before = (
            before
            if isinstance(
                before,
                list,
            )
            else []
        )

        after = (
            after
            if isinstance(
                after,
                list,
            )
            else []
        )

        before_canonical = {
            self._canonical_json(
                item
            )
            for item in before
        }

        after_canonical = {
            self._canonical_json(
                item
            )
            for item in after
        }

        added = [
            deepcopy(item)
            for item in after
            if self._canonical_json(
                item
            )
            not in before_canonical
        ]

        removed = [
            deepcopy(item)
            for item in before
            if self._canonical_json(
                item
            )
            not in after_canonical
        ]

        unchanged = [
            deepcopy(item)
            for item in after
            if self._canonical_json(
                item
            )
            in before_canonical
        ]

        modified = []

        before_by_identity = (
            self._build_identity_map(
                before
            )
        )

        after_by_identity = (
            self._build_identity_map(
                after
            )
        )

        shared_identity_keys = (
            set(
                before_by_identity.keys()
            )
            & set(
                after_by_identity.keys()
            )
        )

        for identity_key in sorted(
            shared_identity_keys,
            key=lambda item: str(item),
        ):

            before_item = (
                before_by_identity[
                    identity_key
                ]
            )

            after_item = (
                after_by_identity[
                    identity_key
                ]
            )

            if (
                self._canonical_json(
                    before_item
                )
                !=
                self._canonical_json(
                    after_item
                )
            ):

                modified.append(
                    {
                        "identity": identity_key,
                        "before": deepcopy(
                            before_item
                        ),
                        "after": deepcopy(
                            after_item
                        ),
                    }
                )

        return {
            "added": added,
            "removed": removed,
            "modified": modified,
            "unchanged": unchanged,
            "summary": {
                "added": len(
                    added
                ),
                "removed": len(
                    removed
                ),
                "modified": len(
                    modified
                ),
                "unchanged": len(
                    unchanged
                ),
                "total_before": len(
                    before
                ),
                "total_after": len(
                    after
                ),
            },
        }

    def _build_identity_map(
        self,
        items,
    ):

        identity_map = {}

        identity_keys = (
            "id",
            "item_id",
            "object_id",
            "project_id",
            "module_id",
            "session_id",
            "decision_id",
            "milestone_id",
            "artifact_id",
            "file_id",
            "change_id",
            "name",
            "key",
        )

        for item in items:

            if not isinstance(
                item,
                dict,
            ):

                continue

            identity = None

            for key in identity_keys:

                if (
                    key in item
                    and item[key]
                    is not None
                ):

                    identity = (
                        f"{key}:{item[key]}"
                    )

                    break

            if identity:

                identity_map[
                    identity
                ] = item

        return identity_map

    def _diff_set_items(
        self,
        before,
        after,
    ):

        before = set(
            before or []
        )

        after = set(
            after or []
        )

        added = sorted(
            list(
                after
                - before
            ),
            key=lambda item: str(item),
        )

        removed = sorted(
            list(
                before
                - after
            ),
            key=lambda item: str(item),
        )

        unchanged = sorted(
            list(
                before
                & after
            ),
            key=lambda item: str(item),
        )

        return {
            "added": deepcopy(
                added
            ),
            "removed": deepcopy(
                removed
            ),
            "modified": [],
            "unchanged": deepcopy(
                unchanged
            ),
            "summary": {
                "added": len(
                    added
                ),
                "removed": len(
                    removed
                ),
                "modified": 0,
                "unchanged": len(
                    unchanged
                ),
                "total_before": len(
                    before
                ),
                "total_after": len(
                    after
                ),
            },
        }

    def _build_item_change_details(
        self,
        before,
        after,
    ):

        if (
            isinstance(
                before,
                list,
            )
            and
            isinstance(
                after,
                list,
            )
        ):

            return self._diff_list_items(
                before,
                after,
            )

        if (
            isinstance(
                before,
                set,
            )
            and
            isinstance(
                after,
                set,
            )
        ):

            return self._diff_set_items(
                before,
                after,
            )

        return None

    # =========================================================
    # DEEP DIFF
    # =========================================================

    def _diff_dicts(
        self,
        before,
        after,
        path="",
    ):

        changes = []

        before = (
            before
            if isinstance(
                before,
                dict,
            )
            else {}
        )

        after = (
            after
            if isinstance(
                after,
                dict,
            )
            else {}
        )

        keys = sorted(
            set(
                before.keys()
            )
            |
            set(
                after.keys()
            ),
            key=lambda item: str(item),
        )

        for key in keys:

            current_path = (
                f"{path}.{key}"
                if path
                else str(key)
            )

            before_exists = (
                key
                in before
            )

            after_exists = (
                key
                in after
            )

            old_value = (
                before.get(
                    key
                )
                if before_exists
                else None
            )

            new_value = (
                after.get(
                    key
                )
                if after_exists
                else None
            )

            if (
                not before_exists
                or not after_exists
            ):

                change_type = (
                    self._classify_change(
                        key,
                        old_value,
                        new_value,
                        before_exists,
                        after_exists,
                    )
                )

                changes.append(
                    {
                        "path": current_path,
                        "key": str(key),
                        "change_type": change_type,
                        "before": deepcopy(
                            old_value
                        ),
                        "after": deepcopy(
                            new_value
                        ),
                    }
                )

                continue

            if (
                isinstance(
                    old_value,
                    dict,
                )
                and
                isinstance(
                    new_value,
                    dict,
                )
            ):

                nested_changes = (
                    self._diff_dicts(
                        old_value,
                        new_value,
                        current_path,
                    )
                )

                changes.extend(
                    nested_changes
                )

                continue

            if (
                isinstance(
                    old_value,
                    list,
                )
                and
                isinstance(
                    new_value,
                    list,
                )
            ):

                if (
                    old_value
                    !=
                    new_value
                ):

                    change_type = (
                        self._classify_change(
                            key,
                            old_value,
                            new_value,
                        )
                    )

                    change_record = {
                        "path": current_path,
                        "key": str(key),
                        "change_type": change_type,
                        "before": deepcopy(
                            old_value
                        ),
                        "after": deepcopy(
                            new_value
                        ),
                    }

                    item_changes = (
                        self._build_item_change_details(
                            old_value,
                            new_value,
                        )
                    )

                    if item_changes:

                        change_record[
                            "item_changes"
                        ] = item_changes

                    changes.append(
                        change_record
                    )

                continue

            if (
                isinstance(
                    old_value,
                    set,
                )
                and
                isinstance(
                    new_value,
                    set,
                )
            ):

                if (
                    old_value
                    !=
                    new_value
                ):

                    change_type = (
                        self._classify_change(
                            key,
                            old_value,
                            new_value,
                        )
                    )

                    change_record = {
                        "path": current_path,
                        "key": str(key),
                        "change_type": change_type,
                        "before": deepcopy(
                            old_value
                        ),
                        "after": deepcopy(
                            new_value
                        ),
                    }

                    item_changes = (
                        self._build_item_change_details(
                            old_value,
                            new_value,
                        )
                    )

                    if item_changes:

                        change_record[
                            "item_changes"
                        ] = item_changes

                    changes.append(
                        change_record
                    )

                continue

            if (
                old_value
                !=
                new_value
            ):

                change_type = (
                    self._classify_change(
                        key,
                        old_value,
                        new_value,
                    )
                )

                changes.append(
                    {
                        "path": current_path,
                        "key": str(key),
                        "change_type": change_type,
                        "before": deepcopy(
                            old_value
                        ),
                        "after": deepcopy(
                            new_value
                        ),
                    }
                )

        return changes

    # =========================================================
    # CHANGE DETECTION
    # =========================================================

    def detect_fundamental_changes(
        self,
        changes,
    ):

        return [
            change
            for change in changes
            if change.get(
                "change_type"
            )
            == "FUNDAMENTAL"
        ]

    def detect_structural_changes(
        self,
        changes,
    ):

        return [
            change
            for change in changes
            if change.get(
                "change_type"
            )
            == "STRUCTURAL"
        ]

    def detect_item_additions(
        self,
        changes,
    ):

        additions = []

        for change in changes:

            item_changes = (
                change.get(
                    "item_changes",
                    {},
                )
            )

            for item in (
                item_changes.get(
                    "added",
                    [],
                )
            ):

                additions.append(
                    {
                        "path": change.get(
                            "path"
                        ),
                        "key": change.get(
                            "key"
                        ),
                        "item": deepcopy(
                            item
                        ),
                    }
                )

        return additions

    def detect_item_removals(
        self,
        changes,
    ):

        removals = []

        for change in changes:

            item_changes = (
                change.get(
                    "item_changes",
                    {},
                )
            )

            for item in (
                item_changes.get(
                    "removed",
                    [],
                )
            ):

                removals.append(
                    {
                        "path": change.get(
                            "path"
                        ),
                        "key": change.get(
                            "key"
                        ),
                        "item": deepcopy(
                            item
                        ),
                    }
                )

        return removals

    def detect_item_modifications(
        self,
        changes,
    ):

        modifications = []

        for change in changes:

            item_changes = (
                change.get(
                    "item_changes",
                    {},
                )
            )

            for item in (
                item_changes.get(
                    "modified",
                    [],
                )
            ):

                modifications.append(
                    {
                        "path": change.get(
                            "path"
                        ),
                        "key": change.get(
                            "key"
                        ),
                        "item": deepcopy(
                            item
                        ),
                    }
                )

        return modifications

    def detect_unchanged_items(
        self,
        changes,
    ):

        unchanged = []

        for change in changes:

            item_changes = (
                change.get(
                    "item_changes",
                    {},
                )
            )

            for item in (
                item_changes.get(
                    "unchanged",
                    [],
                )
            ):

                unchanged.append(
                    {
                        "path": change.get(
                            "path"
                        ),
                        "key": change.get(
                            "key"
                        ),
                        "item": deepcopy(
                            item
                        ),
                    }
                )

        return unchanged

    # =========================================================
    # SNAPSHOT COMPARISON
    # =========================================================

    def compare_snapshots(
        self,
        before,
        after,
    ):

        before = (
            before
            if before is not None
            else {}
        )

        after = (
            after
            if after is not None
            else {}
        )

        before_fingerprint = (
            self._fingerprint(
                before
            )
        )

        after_fingerprint = (
            self._fingerprint(
                after
            )
        )

        if (
            before_fingerprint
            ==
            after_fingerprint
        ):

            return {
                "changed": False,
                "before_fingerprint":
                    before_fingerprint,
                "after_fingerprint":
                    after_fingerprint,
                "changes": [],
                "fundamental_changes": [],
                "structural_changes": [],
                "item_additions": [],
                "item_removals": [],
                "item_modifications": [],
                "unchanged_items": [],
                "summary": {
                    "total_changes": 0,
                    "added": 0,
                    "removed": 0,
                    "modified": 0,
                    "fundamental": 0,
                    "structural": 0,
                    "item_added": 0,
                    "item_removed": 0,
                    "item_modified": 0,
                    "item_unchanged": 0,
                },
            }

        changes = (
            self._diff_dicts(
                before,
                after,
            )
        )

        fundamental_changes = (
            self.detect_fundamental_changes(
                changes
            )
        )

        structural_changes = (
            self.detect_structural_changes(
                changes
            )
        )

        item_additions = (
            self.detect_item_additions(
                changes
            )
        )

        item_removals = (
            self.detect_item_removals(
                changes
            )
        )

        item_modifications = (
            self.detect_item_modifications(
                changes
            )
        )

        unchanged_items = (
            self.detect_unchanged_items(
                changes
            )
        )

        summary = {
            "total_changes": len(
                changes
            ),
            "added": sum(
                1
                for item in changes
                if item[
                    "change_type"
                ]
                == "ADDED"
            ),
            "removed": sum(
                1
                for item in changes
                if item[
                    "change_type"
                ]
                == "REMOVED"
            ),
            "modified": sum(
                1
                for item in changes
                if item[
                    "change_type"
                ]
                == "MODIFIED"
            ),
            "fundamental": len(
                fundamental_changes
            ),
            "structural": len(
                structural_changes
            ),
            "item_added": len(
                item_additions
            ),
            "item_removed": len(
                item_removals
            ),
            "item_modified": len(
                item_modifications
            ),
            "item_unchanged": len(
                unchanged_items
            ),
        }

        return {
            "changed": True,
            "before_fingerprint":
                before_fingerprint,
            "after_fingerprint":
                after_fingerprint,
            "changes": changes,
            "fundamental_changes":
                fundamental_changes,
            "structural_changes":
                structural_changes,
            "item_additions":
                item_additions,
            "item_removals":
                item_removals,
            "item_modifications":
                item_modifications,
            "unchanged_items":
                unchanged_items,
            "summary": summary,
        }

    # =========================================================
    # CHANGE EVENT
    # =========================================================

    def create_change_event(
        self,
        before,
        after,
        session_id=None,
        decision_ids=None,
        description="",
        source="unknown",
        affected_files=None,
        related_goals=None,
        related_artifacts=None,
    ):

        comparison = (
            self.compare_snapshots(
                before,
                after,
            )
        )

        change_id = (
            "CHG-"
            + datetime.now(
                timezone.utc
            ).strftime(
                "%Y%m%d%H%M%S%f"
            )
        )

        return {
            "change_id": change_id,
            "project_id": self.project_id,
            "engine_version": self.VERSION,
            "timestamp": self._now(),
            "session_id": session_id,
            "description": description,
            "source": source,
            "affected_files": (
                affected_files or []
            ),
            "related_goals": (
                related_goals or []
            ),
            "related_artifacts": (
                related_artifacts or []
            ),
            "decision_ids": (
                decision_ids or []
            ),
            "before_fingerprint":
                comparison[
                    "before_fingerprint"
                ],
            "after_fingerprint":
                comparison[
                    "after_fingerprint"
                ],
            "changed": comparison[
                "changed"
            ],
            "summary": comparison[
                "summary"
            ],
            "fundamental_changes":
                comparison[
                    "fundamental_changes"
                ],
            "structural_changes":
                comparison[
                    "structural_changes"
                ],
            "item_additions":
                comparison[
                    "item_additions"
                ],
            "item_removals":
                comparison[
                    "item_removals"
                ],
            "item_modifications":
                comparison[
                    "item_modifications"
                ],
            "unchanged_items":
                comparison[
                    "unchanged_items"
                ],
            "changes": comparison[
                "changes"
            ],
            "before_snapshot": deepcopy(
                before
            ),
            "after_snapshot": deepcopy(
                after
            ),
        }

    # =========================================================
    # PERSIST CHANGE
    # =========================================================

    def record_change(
        self,
        event,
    ):

        if not event:

            return {
                "status": "INVALID_EVENT"
            }

        if not event.get(
            "change_id"
        ):

            return {
                "status": "INVALID_EVENT",
                "reason": "missing_change_id",
            }

        change_log = (
            self._load_json(
                self.change_log_path
            )
        )

        if not change_log:

            change_log = (
                self._default_change_log()
            )

        existing_ids = {
            item.get(
                "change_id"
            )
            for item in change_log.get(
                "changes",
                [],
            )
        }

        if (
            event.get(
                "change_id"
            )
            in existing_ids
        ):

            return {
                "status":
                    "DUPLICATE_CHANGE",
                "change_id":
                    event.get(
                        "change_id"
                    ),
            }

        change_log[
            "changes"
        ].append(
            event
        )

        self._save_json(
            self.change_log_path,
            change_log,
        )

        self._save_json(
            self.latest_change_path,
            event,
        )

        self._update_index(
            event
        )

        self._write_markdown_history(
            change_log
        )

        return {
            "status": "RECORDED",
            "change_id": event.get(
                "change_id"
            ),
        }

    # =========================================================
    # INDEX
    # =========================================================

    def _update_index(
        self,
        event,
    ):

        index = (
            self._load_json(
                self.change_index_path
            )
        )

        # =====================================================
        # BACKWARD-COMPATIBLE INDEX SCHEMA
        # =====================================================

        index.setdefault("total_events", 0)
        index.setdefault("total_changes", 0)

        index.setdefault("item_added", 0)
        index.setdefault("item_removed", 0)
        index.setdefault("item_modified", 0)
        index.setdefault("item_unchanged", 0)

        index.setdefault("sessions", {})
        index.setdefault("change_types", {})
        index.setdefault("files", {})
        index.setdefault("paths", {})

        # Normalize index schema for backward compatibility.
        if not isinstance(index, dict):
            index = {}

        if not index:
            index = self._default_change_index()

        index.setdefault("total_events", 0)
        index.setdefault("total_changes", 0)
        index.setdefault("item_modified", 0)
        index.setdefault("sessions", {})
        index.setdefault("change_types", {})
        index.setdefault("files", {})
        index.setdefault("paths", {})
        index[
            "total_events"
        ] += 1

        event_summary = (
            event.get(
                "summary",
                {},
            )
        )

        event_total_changes = (
            event_summary.get(
                "total_changes",
                0,
            )
        )

        index[
            "total_changes"
        ] += event_total_changes

        session_id = (
            event.get(
                "session_id"
            )
        )

        if session_id:

            index[
                "sessions"
            ].setdefault(
                session_id,
                0,
            )

            index[
                "sessions"
            ][session_id] += 1

        for change in event.get(
            "changes",
            [],
        ):

            change_type = (
                change.get(
                    "change_type"
                )
            )

            index[
                "change_types"
            ].setdefault(
                change_type,
                0,
            )

            index[
                "change_types"
            ][change_type] += 1

            path = (
                change.get(
                    "path"
                )
            )

            if path:

                index[
                    "files"
                ].setdefault(
                    path,
                    0,
                )

                index[
                    "files"
                ][path] += 1

                index[
                    "paths"
                ].setdefault(
                    path,
                    {
                        "total_changes": 0,
                        "added": 0,
                        "removed": 0,
                        "modified": 0,
                        "fundamental": 0,
                        "structural": 0,

                        "item_added": 0,
                        "item_removed": 0,
                        "item_modified": 0,
                        "item_unchanged": 0,
                    },
                )

                path_stats = (
                    index[
                        "paths"
                    ][path]
                )

                path_stats[
                    "total_changes"
                ] += 1

                if (
                    change_type
                    == "ADDED"
                ):

                    path_stats[
                        "added"
                    ] += 1

                elif (
                    change_type
                    == "REMOVED"
                ):

                    path_stats[
                        "removed"
                    ] += 1

                elif (
                    change_type
                    == "MODIFIED"
                ):

                    path_stats[
                        "modified"
                    ] += 1

                elif (
                    change_type
                    == "FUNDAMENTAL"
                ):

                    path_stats[
                        "fundamental"
                    ] += 1

                elif (
                    change_type
                    == "STRUCTURAL"
                ):

                    path_stats[
                        "structural"
                    ] += 1

            item_changes = (
                change.get(
                    "item_changes",
                    {},
                )
            )

            item_summary = (
                item_changes.get(
                    "summary",
                    {},
                )
            )

            item_added = (
                item_summary.get(
                    "added",
                    0,
                )
            )

            item_removed = (
                item_summary.get(
                    "removed",
                    0,
                )
            )

            item_modified = (
                item_summary.get(
                    "modified",
                    0,
                )
            )

            item_unchanged = (
                item_summary.get(
                    "unchanged",
                    0,
                )
            )


            index[
                "item_added"
            ] += item_added

            index[
                "item_removed"
            ] += item_removed

            index[
                "item_modified"
            ] += item_modified

            index[
                "item_unchanged"
            ] += item_unchanged

            if path:

                path_stats[
                    "item_added"
                ] += item_added

                path_stats[
                    "item_removed"
                ] += item_removed

                path_stats[
                    "item_modified"
                ] += item_modified

                path_stats[
                    "item_unchanged"
                ] += item_unchanged

        if event.get(
            "fundamental_changes"
        ):

            index[
                "fundamental_changes"
            ] += 1

        if event.get(
            "structural_changes"
        ):

            index[
                "structural_changes"
            ] += 1

        file_change = (
            event.get(
                "file_change"
            )
        )

        if file_change:

            file_path = (
                file_change.get(
                    "path"
                )
            )

            file_change_type = (
                file_change.get(
                    "change_type"
                )
            )

            if file_path:

                index[
                    "files"
                ].setdefault(
                    file_path,
                    0,
                )

                if (
                    file_change_type
                    != "UNCHANGED"
                ):

                    index[
                        "files"
                    ][file_path] += 1

                index[
                    "paths"
                ].setdefault(
                    file_path,
                    {
                        "total_changes": 0,
                        "added": 0,
                        "removed": 0,
                        "modified": 0,
                        "fundamental": 0,
                        "structural": 0,
                        "item_added": 0,
                        "item_removed": 0,
                        "item_modified": 0,
                        "item_unchanged": 0,
                    },
                )

                path_stats = (
                    index[
                        "paths"
                    ][file_path]
                )

                if (
                    file_change_type
                    != "UNCHANGED"
                ):

                    path_stats[
                        "total_changes"
                    ] += 1

                if (
                    file_change_type
                    == "ADDED"
                ):

                    path_stats[
                        "added"
                    ] += 1

                elif (
                    file_change_type
                    == "REMOVED"
                ):

                    path_stats[
                        "removed"
                    ] += 1

                elif (
                    file_change_type
                    == "MODIFIED"
                ):

                    path_stats[
                        "modified"
                    ] += 1

        self._save_json(
            self.change_index_path,
            index,
        )

    # =========================================================
    # MARKDOWN HISTORY
    # =========================================================

    def _format_markdown_item(
        self,
        item,
    ):

        if isinstance(
            item,
            dict,
        ):

            return (
                "```json\n"
                + json.dumps(
                    item,
                    ensure_ascii=False,
                    indent=4,
                )
                + "\n```"
            )

        return (
            f"`{item}`"
        )

    def _write_markdown_history(
        self,
        change_log,
    ):

        lines = [
            "# CRME Change History",
            "",
            f"**Project:** "
            f"{self.project_id}",
            "",
            f"**Engine Version:** "
            f"{self.VERSION}",
            "",
        ]

        for event in reversed(
            change_log.get(
                "changes",
                [],
            )
        ):

            lines.extend(
                [
                    "---",
                    "",
                    f"## "
                    f"{event.get('change_id')}",
                    "",
                    f"- Timestamp: "
                    f"{event.get('timestamp')}",
                    f"- Session: "
                    f"{event.get('session_id')}",
                    f"- Description: "
                    f"{event.get('description')}",
                    f"- Source: "
                    f"{event.get('source')}",
                    "",
                    "### Summary",
                    "",
                ]
            )

            summary = (
                event.get(
                    "summary",
                    {},
                )
            )

            lines.extend(
                [
                    f"- Total change records: "
                    f"{summary.get('total_changes', 0)}",
                    f"- Top-level added: "
                    f"{summary.get('added', 0)}",
                    f"- Top-level removed: "
                    f"{summary.get('removed', 0)}",
                    f"- Modified: "
                    f"{summary.get('modified', 0)}",
                    f"- Fundamental: "
                    f"{summary.get('fundamental', 0)}",
                    f"- Structural: "
                    f"{summary.get('structural', 0)}",
                    f"- Items added: "
                    f"{summary.get('item_added', 0)}",
                    f"- Items removed: "
                    f"{summary.get('item_removed', 0)}",
                    f"- Items modified: "
                    f"{summary.get('item_modified', 0)}",
                    f"- Items unchanged: "
                    f"{summary.get('item_unchanged', 0)}",
                ]
            )

            fundamental_changes = (
                event.get(
                    "fundamental_changes",
                    [],
                )
            )

            if fundamental_changes:

                lines.extend(
                    [
                        "",
                        "### Fundamental Changes",
                        "",
                    ]
                )

                for change in (
                    fundamental_changes
                ):

                    lines.extend(
                        [
                            f"- "
                            f"`{change.get('path')}`",
                            f"  - Before: "
                            f"`{change.get('before')}`",
                            f"  - After: "
                            f"`{change.get('after')}`",
                        ]
                    )

            structural_changes = (
                event.get(
                    "structural_changes",
                    [],
                )
            )

            if structural_changes:

                lines.extend(
                    [
                        "",
                        "### Structural Changes",
                        "",
                    ]
                )

                for change in (
                    structural_changes
                ):

                    lines.extend(
                        [
                            f"- "
                            f"`{change.get('path')}`",
                            f"  - Before: "
                            f"`{change.get('before')}`",
                            f"  - After: "
                            f"`{change.get('after')}`",
                        ]
                    )

            item_additions = (
                event.get(
                    "item_additions",
                    [],
                )
            )

            if item_additions:

                lines.extend(
                    [
                        "",
                        "### Items Added",
                        "",
                    ]
                )

                for item in (
                    item_additions
                ):

                    lines.extend(
                        [
                            f"- "
                            f"`{item.get('path')}`",
                            "  - Added: "
                            + self._format_markdown_item(
                                item.get(
                                    "item"
                                )
                            ),
                        ]
                    )

            item_removals = (
                event.get(
                    "item_removals",
                    [],
                )
            )

            if item_removals:

                lines.extend(
                    [
                        "",
                        "### Items Removed",
                        "",
                    ]
                )

                for item in (
                    item_removals
                ):

                    lines.extend(
                        [
                            f"- "
                            f"`{item.get('path')}`",
                            "  - Removed: "
                            + self._format_markdown_item(
                                item.get(
                                    "item"
                                )
                            ),
                        ]
                    )

            item_modifications = (
                event.get(
                    "item_modifications",
                    [],
                )
            )

            if item_modifications:

                lines.extend(
                    [
                        "",
                        "### Items Modified",
                        "",
                    ]
                )

                for item in (
                    item_modifications
                ):

                    lines.extend(
                        [
                            f"- "
                            f"`{item.get('path')}`",
                            "  - Before: "
                            + self._format_markdown_item(
                                item.get(
                                    "item",
                                ).get(
                                    "before"
                                )
                            ),
                            "  - After: "
                            + self._format_markdown_item(
                                item.get(
                                    "item",
                                ).get(
                                    "after"
                                )
                            ),
                        ]
                    )

            unchanged_items = (
                event.get(
                    "unchanged_items",
                    [],
                )
            )

            if unchanged_items:

                lines.extend(
                    [
                        "",
                        "### Items Unchanged",
                        "",
                    ]
                )

                for item in (
                    unchanged_items
                ):

                    lines.extend(
                        [
                            f"- "
                            f"`{item.get('path')}`",
                            "  - Preserved: "
                            + self._format_markdown_item(
                                item.get(
                                    "item"
                                )
                            ),
                        ]
                    )

            file_change = (
                event.get(
                    "file_change"
                )
            )

            if file_change:

                lines.extend(
                    [
                        "",
                        "### File Change",
                        "",
                        f"- Path: "
                        f"`{file_change.get('path')}`",
                        f"- Type: "
                        f"`{file_change.get('change_type')}`",
                        "",
                        "**Before:**",
                        "",
                        self._format_markdown_item(
                            file_change.get(
                                "before"
                            )
                        ),
                        "",
                        "**After:**",
                        "",
                        self._format_markdown_item(
                            file_change.get(
                                "after"
                            )
                        ),
                    ]
                )

            lines.extend(
                [
                    "",
                    "### Affected Files",
                    "",
                ]
            )

            affected_files = (
                event.get(
                    "affected_files",
                    [],
                )
            )

            if affected_files:

                lines.extend(
                    [
                        f"- "
                        f"`{file_path}`"
                        for file_path
                        in affected_files
                    ]
                )

            else:

                lines.append(
                    "- None recorded"
                )

            lines.extend(
                [
                    "",
                    "### Decisions",
                    "",
                ]
            )

            decision_ids = (
                event.get(
                    "decision_ids",
                    [],
                )
            )

            if decision_ids:

                lines.extend(
                    [
                        f"- "
                        f"`{decision_id}`"
                        for decision_id
                        in decision_ids
                    ]
                )

            else:

                lines.append(
                    "- None recorded"
                )

            lines.extend(
                [
                    "",
                    "### Related Goals",
                    "",
                ]
            )

            related_goals = (
                event.get(
                    "related_goals",
                    [],
                )
            )

            if related_goals:

                lines.extend(
                    [
                        f"- {goal}"
                        for goal
                        in related_goals
                    ]
                )

            else:

                lines.append(
                    "- None recorded"
                )

            lines.extend(
                [
                    "",
                    "### Related Artifacts",
                    "",
                ]
            )

            related_artifacts = (
                event.get(
                    "related_artifacts",
                    [],
                )
            )

            if related_artifacts:

                lines.extend(
                    [
                        f"- "
                        f"`{artifact}`"
                        for artifact
                        in related_artifacts
                    ]
                )

            else:

                lines.append(
                    "- None recorded"
                )

            lines.append(
                ""
            )

        self.change_history_markdown_path.write_text(
            "\n".join(
                lines
            ),
            encoding="utf-8",
        )

    # =========================================================
    # SESSION INTEGRATION
    # =========================================================

    def track_session_transition(
        self,
        session_id,
        before_state,
        after_state,
        decision_ids=None,
        description="",
        affected_files=None,
        related_goals=None,
        related_artifacts=None,
    ):

        event = (
            self.create_change_event(
                before=before_state,
                after=after_state,
                session_id=session_id,
                decision_ids=decision_ids,
                description=description,
                source="session_transition",
                affected_files=affected_files,
                related_goals=related_goals,
                related_artifacts=related_artifacts,
            )
        )

        return self.record_change(
            event
        )

    # =========================================================
    # PROJECT INTEGRATION
    # =========================================================

    def track_project_transition(
        self,
        before_state,
        after_state,
        session_id=None,
        decision_ids=None,
        description="",
        affected_files=None,
        related_goals=None,
        related_artifacts=None,
    ):

        event = (
            self.create_change_event(
                before=before_state,
                after=after_state,
                session_id=session_id,
                decision_ids=decision_ids,
                description=description,
                source="project_transition",
                affected_files=affected_files,
                related_goals=related_goals,
                related_artifacts=related_artifacts,
            )
        )

        return self.record_change(
            event
        )

    # =========================================================
    # FILE SNAPSHOT
    # =========================================================

    def snapshot_file(
        self,
        file_path,
    ):

        file_path = Path(
            file_path
        )

        if not file_path.is_absolute():

            file_path = (
                self.base_path
                / file_path
            )

        if not file_path.exists():

            return {
                "exists": False,
                "path": str(
                    file_path
                ),
            }

        content = (
            file_path.read_bytes()
        )

        stat = (
            file_path.stat()
        )

        return {
            "exists": True,
            "path": str(
                file_path
            ),
            "size": len(
                content
            ),
            "sha256": hashlib.sha256(
                content
            ).hexdigest(),
            "modified_at":
                datetime.fromtimestamp(
                    stat.st_mtime,
                    timezone.utc,
                ).isoformat(),
        }

    # =========================================================
    # FILE CHANGE TRACKING
    # =========================================================

    def track_file_change(
        self,
        file_path,
        before_snapshot,
        after_snapshot,
        session_id=None,
        description="",
    ):

        before_snapshot = (
            before_snapshot or {}
        )

        after_snapshot = (
            after_snapshot or {}
        )

        before_exists = (
            before_snapshot.get(
                "exists",
                False,
            )
        )

        after_exists = (
            after_snapshot.get(
                "exists",
                False,
            )
        )

        if (
            not before_exists
            and after_exists
        ):

            change_type = (
                "ADDED"
            )

        elif (
            before_exists
            and not after_exists
        ):

            change_type = (
                "REMOVED"
            )

        elif (
            before_snapshot.get(
                "sha256"
            )
            !=
            after_snapshot.get(
                "sha256"
            )
        ):

            change_type = (
                "MODIFIED"
            )

        else:

            change_type = (
                "UNCHANGED"
            )

        event = {
            "change_id": (
                "CHG-"
                + datetime.now(
                    timezone.utc
                ).strftime(
                    "%Y%m%d%H%M%S%f"
                )
            ),
            "project_id": self.project_id,
            "engine_version": self.VERSION,
            "timestamp": self._now(),
            "session_id": session_id,
            "description": description,
            "source": "file_tracking",
            "affected_files": [
                str(
                    file_path
                )
            ],
            "file_change": {
                "path": str(
                    file_path
                ),
                "change_type": change_type,
                "before": deepcopy(
                    before_snapshot
                ),
                "after": deepcopy(
                    after_snapshot
                ),
            },
            "summary": {
                "total_changes": (
                    0
                    if (
                        change_type
                        == "UNCHANGED"
                    )
                    else 1
                ),
                "added": (
                    1
                    if (
                        change_type
                        == "ADDED"
                    )
                    else 0
                ),
                "removed": (
                    1
                    if (
                        change_type
                        == "REMOVED"
                    )
                    else 0
                ),
                "modified": (
                    1
                    if (
                        change_type
                        == "MODIFIED"
                    )
                    else 0
                ),
                "fundamental": 0,
                "structural": 0,
                "item_added": 0,
                "item_removed": 0,
                "item_modified": 0,
                "item_unchanged": 0,
            },
            "changes": [],
            "fundamental_changes": [],
            "structural_changes": [],
            "item_additions": [],
            "item_removals": [],
            "item_modifications": [],
            "unchanged_items": [],
            "before_snapshot": deepcopy(
                before_snapshot
            ),
            "after_snapshot": deepcopy(
                after_snapshot
            ),
        }

        return self.record_change(
            event
        )

    # =========================================================
    # QUERY API
    # =========================================================

    def get_all_changes(
        self,
    ):

        log = (
            self._load_json(
                self.change_log_path
            )
        )

        if not log:

            return []

        return log.get(
            "changes",
            [],
        )

    def get_session_changes(
        self,
        session_id,
    ):

        return [
            change
            for change in (
                self.get_all_changes()
            )
            if change.get(
                "session_id"
            )
            == session_id
        ]

    def get_fundamental_changes(
        self,
    ):

        return [
            change
            for change in (
                self.get_all_changes()
            )
            if change.get(
                "fundamental_changes"
            )
        ]

    def get_structural_changes(
        self,
    ):

        return [
            change
            for change in (
                self.get_all_changes()
            )
            if change.get(
                "structural_changes"
            )
        ]

    def get_item_additions(
        self,
    ):

        return [
            change
            for change in (
                self.get_all_changes()
            )
            if change.get(
                "item_additions"
            )
        ]

    def get_item_removals(
        self,
    ):

        return [
            change
            for change in (
                self.get_all_changes()
            )
            if change.get(
                "item_removals"
            )
        ]

    def get_item_modifications(
        self,
    ):

        return [
            change
            for change in (
                self.get_all_changes()
            )
            if change.get(
                "item_modifications"
            )
        ]

    def get_latest_change(
        self,
    ):

        return self._load_json(
            self.latest_change_path
        )

    def get_index(
        self,
    ):

        return self._load_json(
            self.change_index_path
        )

    # =========================================================
    # PATH QUERY
    # =========================================================

    def get_changes_for_path(
        self,
        path,
    ):

        results = []

        for change in (
            self.get_all_changes()
        ):

            for item in change.get(
                "changes",
                [],
            ):

                if (
                    item.get(
                        "path"
                    )
                    == path
                ):

                    results.append(
                        item
                    )

        return results

    # =========================================================
    # RECONSTRUCTION
    # =========================================================

    def reconstruct_state(
        self,
        change_id=None,
    ):

        changes = (
            self.get_all_changes()
        )

        if not changes:

            return None

        if change_id:

            selected = None

            for event in changes:

                if (
                    event.get(
                        "change_id"
                    )
                    == change_id
                ):

                    selected = event

                    break

            if selected is None:

                return None

            return deepcopy(
                selected.get(
                    "after_snapshot"
                )
            )

        latest = (
            changes[-1]
        )

        return deepcopy(
            latest.get(
                "after_snapshot"
            )
        )

    def reconstruct_state_at(
        self,
        timestamp=None,
        change_id=None,
    ):

        changes = (
            self.get_all_changes()
        )

        if not changes:

            return None

        if change_id:

            for event in changes:

                if (
                    event.get(
                        "change_id"
                    )
                    == change_id
                ):

                    return deepcopy(
                        event.get(
                            "after_snapshot"
                        )
                    )

            return None

        if timestamp is None:

            return self.reconstruct_state()

        selected_event = None

        for event in changes:

            event_timestamp = (
                event.get(
                    "timestamp"
                )
            )

            if (
                event_timestamp
                is None
            ):

                continue

            if (
                event_timestamp
                <= timestamp
            ):

                selected_event = event

        if selected_event is None:

            return None

        return deepcopy(
            selected_event.get(
                "after_snapshot"
            )
        )

    # =========================================================
    # SUMMARY
    # =========================================================

    def summary(
        self,
    ):

        index = (
            self.get_index()
        )

        if not index:

            return {
                "project_id":
                    self.project_id,
                "engine_version":
                    self.VERSION,
                "total_changes": 0,
                "total_events": 0,
                "fundamental_changes": 0,
                "structural_changes": 0,
                "sessions_with_changes": 0,
                "change_types": {},
                "tracked_paths": 0,
                "item_added": 0,
                "item_removed": 0,
                "item_modified": 0,
                "item_unchanged": 0,
            }

        return {
            "project_id":
                self.project_id,
            "engine_version":
                self.VERSION,
            "total_changes":
                index.get(
                    "total_changes",
                    0,
                ),
            "total_events":
                index.get(
                    "total_events",
                    0,
                ),
            "fundamental_changes":
                index.get(
                    "fundamental_changes",
                    0,
                ),
            "structural_changes":
                index.get(
                    "structural_changes",
                    0,
                ),
            "sessions_with_changes":
                len(
                    index.get(
                        "sessions",
                        {},
                    )
                ),
            "change_types":
                index.get(
                    "change_types",
                    {},
                ),
            "tracked_paths":
                len(
                    index.get(
                        "files",
                        {},
                    )
                ),
            "item_added":
                index.get(
                    "item_added",
                    0,
                ),
            "item_removed":
                index.get(
                    "item_removed",
                    0,
                ),
            "item_modified":
                index.get(
                    "item_modified",
                    0,
                ),
            "item_unchanged":
                index.get(
                    "item_unchanged",
                    0,
                ),
        }


if __name__ == "__main__":

    engine = ChangeTrackingEngine()

    print(
        json.dumps(
            engine.summary(),
            indent=4,
            ensure_ascii=False,
        )
    )

