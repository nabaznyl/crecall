# Mutation Testing — Plan and Recommendations

Purpose
-------
This document describes a pragmatic rollout plan for mutation testing in the `crecall` project. Mutation testing increases test-suite quality by introducing small, systematic code changes (mutants) and checking whether the tests detect them. Surviving mutants highlight gaps in assertions or behavior validation.

Goals
-----
- Establish a low-friction mutation-testing process developers can run locally.
- Run a nightly, constrained mutation-test job in CI to catch regressions in test quality.
- Provide clear triage and remediation guidance for surviving mutants.

Tools Considered
---------------
- `mutmut` — popular, simple to adopt, fast iterative workflow for developers. Good first-step tool for local use and nightly CI runs.
- `cosmic-ray` — more configurable and parallel, useful for larger, long-running mutation campaigns; higher operational overhead.

Recommended Approach
--------------------
1. Start with `mutmut` as the primary tool:
   - Easy to install (`pip install mutmut`) and integrate with local workflows.
   - Supports incremental runs and provides simple commands to inspect surviving mutants.
2. Offer `cosmic-ray` as an optional follow-up for periodic deep analysis if desired.

Local Developer Workflow (mutmut)
--------------------------------
- Install locally (ideally in the dev/test extras or a `dev-requirements.txt`):
  ```bash
  python -m pip install --upgrade pip
  pip install "mutmut>=2.2"
  ```
- Run quick mutation run over primary app code (example, adjust paths):
  ```bash
  # run tests and create mutants; -j auto uses multiple workers
  mutmut run --paths-to-mutate backend/app -j auto

  # show results (killed/survived/memory errors)
  mutmut results

  # reproduce a surviving mutant (replace <id> with the shown mutant id)
  mutmut show <id>
  mutmut --line <line> show <id>
  ```

Mutmut tips
-----------
- Use `mutmut run --use-coverage` to limit mutation sites to covered code when you want faster results tied to existing tests.
- Exclude generated files, migrations, and third-party code by narrowing `--paths-to-mutate` (do *not* run on `venv`/`site-packages`).
- Persist `mutmut` cache (`.mutmut-cache`) in workspace for incremental runs; add to `.gitignore`.

CI Strategy (practical, resource-conscious)
-----------------------------------------
- Mutation testing is expensive; run a constrained job nightly rather than on every PR. Suggested pipeline:
  - Workflow name: `mutation-testing.yml` (trigger: `workflow_dispatch` + `schedule: cron: '0 3 * * *'` UTC nightly)
  - Python: single job on a representative interpreter (e.g., `3.11`) to limit run-time.
  - Install dev dependencies including `mutmut` and the project's test requirements.
  - Run `mutmut` with a time cap and limited paths:
    ```bash
    pip install -r backend/requirements-dev.txt  # include mutmut here
    mutmut run --paths-to-mutate backend/app --use-coverage -j 2
    mutmut results --show-only-survived > mutation-results.txt
    ```
  - Upload `mutation-results.txt` as a build artifact for triage.
  - Optionally, fail the workflow if the mutation score drops below a threshold (see thresholds below).

Example GitHub Actions job snippet
---------------------------------
```yaml
name: Mutation Testing (nightly)
on:
  schedule:
    - cron: '0 3 * * *'
  workflow_dispatch:

jobs:
  mutation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dev deps
        run: |
          python -m pip install --upgrade pip
          pip install -r backend/requirements-dev.txt
      - name: Run mutmut (constrained)
        run: |
          mutmut run --paths-to-mutate backend/app --use-coverage -j 2 || true
          mutmut results --show-only-survived > mutation-results.txt || true
      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: mutation-results
          path: mutation-results.txt
```

Thresholds & Acceptance Criteria
--------------------------------
- Start with an advisory threshold: require mutation coverage (killed mutants / total applicable mutants) >= 70% as a soft gate. For critical modules, aim for >= 85%.
- Do not make the nightly job block merges initially; instead, surface artifacts and notifications so teams can triage.

Triage Workflow
----------------
- Inspect `mutation-results.txt` and run `mutmut show <id>` locally to see the exact mutant and failing assertion.
- Common fixes:
  - Strengthen or add assertions in tests.
  - Add property-based tests or additional scenarios to cover edge cases.
  - If the code is intentionally tolerant (e.g., defensive return), add an explicit assertion or mark the mutant as `ignored` temporarily.

Operational Notes & Caveats
--------------------------
- Mutation testing can be flaky where tests depend on timing, external services, or global state. Prefer running with deterministic test-run options and isolated test databases.
- Avoid running mutation tests on all matrix Python versions; pick a single representative version for nightly runs to control cost.
- Keep mutation runs incremental (`.mutmut-cache`) to reduce runtime for nightly jobs.

Next Steps (implementation plan)
--------------------------------
1. Add `mutmut` to `backend/requirements-dev.txt` (or `pyproject.toml` dev extras).
2. Add `.mutmut-cache` to `.gitignore`.
3. Create `docs/FEATURES/mutation-testing.md` (this file).
4. Add the `mutation-testing.yml` workflow (nightly + workflow_dispatch) that uploads `mutation-results.txt` as an artifact.
5. After a few nights of run data, decide whether to: (a) raise the advisory threshold, (b) add targeted mutation tests to critical modules, or (c) introduce `cosmic-ray` for deep runs.

References & Links
------------------
- mutmut: https://mutmut.readthedocs.io/
- cosmic-ray: https://cosmic-ray.readthedocs.io/

Contact / Ownership
-------------------
- Suggested owner for first implementation: backend/QA or a backend maintainer. They will:
  - Add `mutmut` to dev deps, create the CI workflow, and tune the paths/time budget.
  - Review nightly artifacts and prioritize remediation.

Appendix: Quick commands
------------------------
- Run full mutmut (local): `mutmut run --paths-to-mutate backend/app -j auto`
- Show results: `mutmut results`
- Show a mutant detail: `mutmut show <id>`
- Re-run single mutant (to reproduce failure): `mutmut --line <line> run <id>`
