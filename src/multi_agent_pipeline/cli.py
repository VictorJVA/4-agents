from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from .orchestrator import run_pipeline


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a 4-agent software engineering artifact pipeline with Groq."
    )
    parser.add_argument(
        "--input-file",
        type=Path,
        required=True,
        help="Path to input JSON file containing: {\"brief_text\": \"...\"}",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        default=Path("final_artifacts.json"),
        help="Where to write final artifacts JSON.",
    )
    parser.add_argument(
        "--provider",
        choices=["groq", "gemini"],
        default=None,
        help="LLM provider (default: gemini if GEMINI_API_KEY set, else groq).",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Model name (default: gemini-2.0-flash for Gemini, llama-3.1-8b-instant for Groq).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    payload = json.loads(args.input_file.read_text(encoding="utf-8"))
    brief_text = payload.get("brief_text")
    if not isinstance(brief_text, str):
        raise ValueError("Input JSON must include a string field 'brief_text'.")

    progress_payload: dict[str, Any] = {
        "initial_brief": {"brief_text": brief_text},
    }

    def _print_agent_output(agent_name: str, output: BaseModel) -> None:
        print(f"\n=== {agent_name} ===", flush=True)
        print(output.model_dump_json(indent=2), flush=True)

        # Persist each agent output as soon as it is produced.
        progress_payload[agent_name] = output.model_dump()
        per_agent_file = args.output_file.with_name(f"{agent_name}.json")
        per_agent_file.write_text(
            output.model_dump_json(indent=2),
            encoding="utf-8",
        )
        args.output_file.write_text(
            json.dumps(progress_payload, indent=2, ensure_ascii=True),
            encoding="utf-8",
        )

    artifacts = run_pipeline(
        brief_text=brief_text,
        provider=args.provider,
        model=args.model,
        on_agent_complete=_print_agent_output,
    )
    args.output_file.write_text(
        artifacts.model_dump_json(indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
