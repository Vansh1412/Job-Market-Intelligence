# M0 Test Baseline

Run date: 2026-11-03 local snapshot. Commands were selected from package scripts and the current CI workflow. Build output/cache artifacts are ignored by Git.

| Area | Exact command | Result |
|---|---|---|
| Backend CI code/schema/cloud subset | `python -m pytest tests/test_routing_contracts.py tests/test_schema_contracts.py tests/test_cloud_contracts.py -v` | **17 passed, 0 failed, 0 skipped, 1.70s.** Verified executed. Python 3.13.9, pytest 8.4.2, Windows. |
| Backend full suite | `python -m pytest -vv` | **Not completed.** Pytest stayed at `collecting ...` for >60 seconds with no collected test list, then was interrupted. No test outcomes can be inferred. A prior `python -m pytest -q` also produced no output and did not complete within the observation window. |
| Frontend Vitest | `npm test -- --reporter=dot` | **0 test files / 0 tests executed; 3 worker startup errors.** Fork workers timed out after 60s before executing tests. |
| Frontend lint | `npm run lint` | Exit 0. Oxlint emitted 89 warnings: unused imports/locals, React fast-refresh export warning, missing hook dependencies, setState-in-effect, unstable memo dependencies. No lint errors reported. |
| Frontend build + TS check | `npm run build` | Exit 0. `tsc -b` passed and Vite 8.3.3 built 2,891 modules. Main assets: JS 276.91 kB, Recharts chunk 374.34 kB (raw); gzipped main 71.83 kB and charts 107.64 kB. |
| Python compileall | not run | CI workflow defines `python -m compileall src/`; not independently executed in this audit. |
| Security/governance workflow | inspected only | Workflow path checks exist; live workflow status not inspected. |

The initial attempt to run the full backend suite was stopped after it did not finish collection. It is an **environment/runtime execution limitation**, not a confirmed code failure. The CI subset passed but does not cover model inference, integration, data QA, or every frontend path. Frontend tests remain unverified due worker startup timeout. No expectations/source were changed to obtain these results.

Test inventory under `tests/`: archetype parity, chart contracts, cloud contracts, end-to-end integration, golden predictions, input validation, market analytics, prediction parity, routing contracts, schema contracts, skill integrity, zero-storage deployment; frontend: calculator, routing, skills contract.

