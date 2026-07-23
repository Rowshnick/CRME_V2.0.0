import json

from core.change_tracking_engine import ChangeTrackingEngine


def main():
    engine = ChangeTrackingEngine(
        base_path=".",
        project_id="CRME-001",
    )

    before = {
        "project_goal": "Build CRME Research Core",
        "evaluation_protocol": "single_run",
        "paper_claims": {
            "evaluation": "basic evaluation",
        },
        "files": [
            "core/memory_engine.py",
            "core/session_engine.py",
            "evaluation/evaluation_engine.py",
        ],
        "modules": [
            "memory_engine",
            "session_engine",
            "project_engine",
        ],
    }

    after = {
        "project_goal": "Build CRME Research Memory and Evaluation System",
        "evaluation_protocol": "multi_run_statistical_evaluation",
        "paper_claims": {
            "evaluation": "statistically validated multi-run evaluation",
        },
        "files": [
            "core/memory_engine.py",
            "core/session_engine.py",
            "core/change_tracking_engine.py",
        ],
        "modules": [
            "memory_engine",
            "session_engine",
            "project_engine",
            "change_tracking_engine",
        ],
    }

    result = engine.compare_snapshots(
        before,
        after,
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
