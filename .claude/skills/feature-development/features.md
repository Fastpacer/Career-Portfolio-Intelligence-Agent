# Feature backlog

Priority: P1 = highest user value per unit of effort. Status: `todo` / `in-progress` / `done`.

---

## F-1 Structured scorecard with visual dashboard (P1, todo)
**Why:** The four scores are the headline output, but today they're buried in prose and unverifiable.
**Design:** `CareerReport.scores: Scores{ats, portfolio, skill_alignment, overall}`, each with `value: int (0–100)` and `rationale: str`. Streamlit shows them in an `st.metric` row and a radar chart (plotly). The overall score is computed deterministically, as a weighted mean, rather than asked from the LLM, so it stays consistent.
**Depends on:** Phase 2 structured output.

## F-2 Job-description matching (P1, todo)
**Why:** "Target role" is just a free-text label. Matching against a real JD gives much sharper gaps.
**Design:** Add an optional JD text area or URL. A deterministic stage extracts and normalizes skills from the JD and the CV (a curated synonym map, e.g. "k8s" → "kubernetes") and computes coverage: matched, missing, and extra. The LLM gets the diff and explains the priorities. The ATS score uses the keyword coverage.
**Depends on:** F-1.

## F-3 Deep GitHub signal analysis (P1, todo)
**Why:** Stars and descriptions say little about engineering quality.
**Design:** For the top N owned, non-fork repos, fetch the README (length, setup instructions, badges), `/languages` byte counts, topics, the last commit date, and whether tests, CI or a license are present (look for `tests/`, `.github/workflows`, `LICENSE`). Score each repo on a deterministic rubric, and have the LLM comment only on the top 3. Respect rate limits: requires `GITHUB_TOKEN` and caches responses for 24 h.
**Depends on:** Phase 2 GitHub client.

## F-4 Report export (P2, todo)
**Why:** Users want to keep and share the report.
**Design:** Add a `st.download_button` for Markdown, which comes straight from the renderer, and for PDF, rendered server-side with `weasyprint` or `markdown-pdf`. On the API, add `GET /reports/{id}?format=md|pdf` once F-6 exists.

## F-5 Streaming output (P2, todo)
**Why:** A 20–40 s blank spinner hurts the UX.
**Design:** Stream the narrative sections with `st.write_stream`. The scores section still waits for the validated JSON. The API exposes an SSE endpoint `POST /analyze/stream`.

## F-6 Analysis history and progress tracking (P2, todo)
**Why:** Users can re-run the analysis after acting on the roadmap and see the improvement.
**Design:** Use SQLite locally and Postgres in production via SQLModel. Store input hashes (not the raw CV, unless the user opts in), the `CareerReport` JSON, and a timestamp. The UI shows score deltas between runs. Roadmap items become checkboxes whose state is persisted.
**Depends on:** F-1. Needs a user identity, which can be as simple as a GitHub username plus a magic-link email or GitHub OAuth.

## F-7 Multi-role comparison (P3, todo)
**Why:** Career switchers want to know which of several roles fits best.
**Design:** Accept 2–3 roles. Fetch GitHub data and parse the CV once, then run the alignment stage for each role in parallel. Show the results as a comparison table.
**Depends on:** F-1, staged pipeline.

## F-8 Resume bullet rewriter (P3, todo)
**Why:** "Improve your resume" advice is far more useful with concrete before/after text.
**Design:** Pick the 5 weakest bullets, using heuristics: no metric, weak verb, longer than 2 lines. The LLM rewrites each one using the STAR or XYZ format and must not invent metrics; where a number is needed, it uses `[X%]` placeholders. Show the results as a side-by-side diff.

## F-9 Prompt evaluation harness (P2, todo, internal)
**Why:** Prompt changes currently can't be tested for regressions.
**Design:** `evals/` holds about 10 anonymized CV and GitHub fixtures with expected properties (score ranges, must-mention skills). A script runs the pipeline against the real model, and an LLM judge checks rubric adherence. It runs manually or nightly, never in the unit-test CI.

## F-10 PII redaction and privacy notice (P2, todo)
**Why:** CVs contain personal data sent to a third-party LLM.
**Design:** A regex pass for emails, phone numbers, and addresses, plus name removal using the CV's header line, applied before prompting. Add a UI notice and a "do not store" default. Links to Phase 3 step 6.
