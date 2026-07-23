import json

from core.change_tracking_engine import ChangeTrackingEngine


def main():
    engine = ChangeTrackingEngine(
        base_path=".",
        project_id="CRME-001",
    )

    before_state = {
        "project_id": "CRME-001",

        "project_goal": "Build CRME Research Core",

        "evaluation_protocol": "single_run",

        "modules": [
            "memory_engine",
            "session_engine",
            "project_engine",
        ],

        "files": [
            "core/memory_engine.py",
            "core/session_engine.py",
            "evaluation/evaluation_engine.py",
        ],

        "paper_claims": {
            "evaluation": "basic evaluation",
        },

        "configuration": {
            "timeout": 30,
        },
    }

    after_state = {
        "project_id": "CRME-001",

        # FUNDAMENTAL CHANGE
        "project_goal": "Build CRME Research Memory and Evaluation System",

        # Currently expected to be MODIFIED
        "evaluation_protocol": "multi_run_statistical_evaluation",

        # STRUCTURAL CHANGE
        "modules": [
            "memory_engine",
            "session_engine",
            "project_engine",
            "change_tracking_engine",
        ],

        # ADDED + REMOVED file paths
        "files": [
            "core/memory_engine.py",
            "core/session_engine.py",
            "core/change_tracking_engine.py",
        ],

        # FUNDAMENTAL CHANGE
        "paper_claims": {
            "evaluation": "statistically validated multi-run evaluation",
        },

        # MODIFIED CHANGE
        "configuration": {
            "timeout": 60,
        },
    }

    result = engine.compare_snapshots(
        before_state,
        after_state,
    )

    print(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

