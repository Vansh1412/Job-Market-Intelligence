# Sprint 2 Test Report

**Status: Sprint 2 tests NOT RUN.** This planning phase made no application-code changes and introduced no tests. No Sprint 2 acceptance criterion is claimed as passed.

## Commands and actual results in this planning phase

| Command/check | Result |
|---|---|
| Repository inspection via `git status --short`, `git rev-parse HEAD`, targeted file reads and `rg` | Completed for baseline audit; no tests run. |
| Official-source web research | Completed for current ONS and Companies House source pages; it is not an application test. |
| Dataset acquisition / parser tests | Not run; no download was authorized or performed. |
| Sprint 2 backend / API / frontend tests | Not run; no implementation exists. |
| Existing India/USA regression tests | Not rerun in this planning phase. Refer to the accepted Sprint 1 test report for prior results; they must be rerun after implementation. |

## Required after implementation approval

Record exact commands and actual collected/passed/failed/skipped counts. Run ingestion unit tests using controlled fixtures; UK service/contract tests; actual HTTP tests through the FastAPI application; existing backend CI subset; India and USA golden prediction tests; model artifact hash comparison; and frontend checks if frontend code is approved. A command that times out or is blocked is not a pass. Do not weaken or skip existing golden assertions.
