# Python evaluator examples

`gemini_sponsor_fit_evaluator.py` is **Troy Bacon's downstream example on his fork, not upstream Langfuse code**. It demonstrates the Python code-evaluation contract exposed by the runner: `EvaluationContext` is read from the observation and experiment payload, and `EvaluationResult(scores=[Score(...)])` is returned.

The example uses deterministic category matching and does not call Gemini or any network service. In a production application, Gemini structured output can be parsed and placed in `observation.output`; the evaluator comment marks the point where that parsed response is scored.

Run the local fixture from the repository root:

```bash
python3 scripts/code-eval-runners/python/examples/gemini_sponsor_fit_evaluator.py
```

The fixture invokes `code_based_eval_handler.handler` directly and should return two matching category scores, one missing category score, and an overall score of `0.6666666666666666`. The file has no third-party dependencies.
