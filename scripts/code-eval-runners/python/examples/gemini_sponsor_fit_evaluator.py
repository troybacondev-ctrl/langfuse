"""Deterministic sponsor-fit evaluator example.

This is Troy Bacon's downstream example on his fork, not upstream Langfuse code.
It is intentionally network-free: a Gemini structured-output response can be
passed in as ``observation.output`` after the application has already parsed it.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


# The code-eval handler injects EvaluationResult and Score into evaluator source.
# Keeping these names unimported here also lets this file be copied as evaluator
# source into the runner, whose deployment package contains only the handler.

def _text(value: Any) -> str:
    return str(value).strip().casefold()


def _categories(value: Any) -> list[str]:
    """Read categories from either the expected fixture or structured output."""
    if isinstance(value, dict):
        value = value.get("categories", [])
    if not isinstance(value, (list, tuple, set)):
        return []
    return [str(category).strip() for category in value if str(category).strip()]


def _slug(value: str) -> str:
    return "_".join(_text(value).replace("-", " ").split())


def evaluate(ctx: "EvaluationContext") -> "EvaluationResult":
    """Score a recommendation's category coverage against the expected categories."""
    observation_output = ctx.observation.output
    expected_output = (
        ctx.experiment.item_expected_output if ctx.experiment is not None else None
    )
    expected = _categories(expected_output)
    actual = {_text(category) for category in _categories(observation_output)}

    scores = []
    for category in expected:
        matched = _text(category) in actual
        scores.append(
            Score(
                value=1 if matched else 0,
                name=f"sponsor_fit.{_slug(category)}",
                data_type="NUMERIC",
                comment=(
                    f"Expected category '{category}' was "
                    f"{'included' if matched else 'not included'} in the recommendation."
                ),
            )
        )

    # Gemini structured-output integration point: evaluate the parsed response
    # above, after Gemini has returned JSON matching the recommendation schema.
    # No Gemini SDK call belongs in this deterministic, network-free evaluator.
    overall = (
        sum(score.value for score in scores) / len(scores) if scores else 0
    )
    scores.append(
        Score(
            value=overall,
            name="sponsor_fit.overall",
            data_type="NUMERIC",
            comment="Fraction of expected sponsor categories covered.",
        )
    )
    return EvaluationResult(scores=scores)


def run_fixture() -> dict[str, Any]:
    """Invoke this evaluator through the real handler contract, without network."""
    handler_path = Path(__file__).resolve().parents[1] / "code_based_eval_handler.py"
    spec = importlib.util.spec_from_file_location("code_based_eval_handler", handler_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load handler from {handler_path}")
    handler_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(handler_module)
    source = Path(__file__).read_text(encoding="utf-8")
    return handler_module.handler(
        {
            "code": {"source": source},
            "payload": {
                "observation": {
                    "output": {
                        "recommendation": "Sponsor the developer conference package",
                        "categories": ["developer tools", "community"],
                    }
                },
                "experiment": {
                    "itemExpectedOutput": {
                        "categories": ["Developer Tools", "Community", "Sustainability"]
                    }
                },
            },
        },
        None,
    )


if globals().get("__name__") == "__main__":
    print(run_fixture())
