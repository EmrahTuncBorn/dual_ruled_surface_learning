# Learning ruled surfaces as dual spherical curves

A ruled surface is the trace of a moving line; in the language of the E. Study map it is a curve
on the dual unit sphere. This repository tests, with cheap network-free experiments first, whether
that classical language helps a learning system:

- **Phase 0 (done).** Does writing output lines as dual unit vectors (A) fit point clouds better than
  base point + direction (B) or two endpoints (C)? **No:** A was significantly worse than C in final
  Chamfer error (geometric-mean ratio 1.34) and convergence speed; the ordering held on a wider
  learning-rate grid. The representation axis is weak.
- **Phase 1 (in progress).** In Plücker coordinates the coplanarity of consecutive lines is *linear* in
  the next moment, so developability can be enforced exactly by a closed-form, differentiable
  projection (a "hard developability layer"). Does this cost fitting accuracy compared with penalty
  terms that reach the same developability level?

The design documents are in Turkish (`docs/tarif_v3.md`, `PROGRESS.md`); code and docstrings are in English.

## Setup

Python 3.12, CPU is enough for Phases 0 and 1.

```
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
.venv/Scripts/python -m pip install -e . --no-deps
```

The editable install makes the `ruled` package importable from anywhere; the experiment scripts are run
as files from the repository root. (On Linux/macOS use `.venv/bin/python`.)

## Running

```
python -m pytest                                # sanity tests (v2 Section 14.7, v3 Section 7.2)
python experiments/phase0.py timing             # time per optimisation step
python experiments/phase0.py all                # Phase 0: validation sweep, selection, test runs
python experiments/phase0_analyze.py            # Phase 0 decision report
python experiments/phase0_lrext.py              # exploratory wider learning-rate check
python experiments/phase1_tau.py                # developability threshold tau of Phase 1
```

Runs are resumable (each unit of work is written atomically to its own file and skipped when present)
and a results directory is bound to one git commit: a dirty tree or a different commit is refused.

## Layout

```
ruled/            core package
  geometry.py     dual normalisation, sign alignment, interpolation, hard layer, angle defect
  reps.py         representations A, B, C and H (A with the hard layer)
  losses.py       Chamfer (KD-tree matching), smoothness, developability penalties, samplers
  data.py         synthetic patches: general, cylinder, cone, tangent developable, hyperbolic paraboloid
experiments/      phase scripts (results go to results/, which is not versioned)
results_summary/  small summary files of finished runs (reports, selections, logs)
tests/            sanity tests
docs/             v2 specification (.docx) and v3 specification (tarif_v3.md)
PROGRESS.md       pre-registrations, deviations, results and log (Turkish)
GLOSSARY.md       Turkish-English terms and notation rules
RELATED_WORK.md   references and their verification status
```

## Status

The project was closed after Phase 1b (2026-10-13). Both pre-registered decisions were negative; see the
closing report `docs/kapanis_raporu.md` (Turkish) and `PROGRESS.md`.

| Phase | Content | Status |
|---|---|---|
| 0 | Network-free representation experiment | done: representation axis weak |
| 1a | Hard layer, angle-defect metric, penalties, tests | done: 42 tests pass, tau = 0.00756 |
| 1b | Network-free developability experiment | done: weak (median angle defect of H 1.134 > tau) |
| 2 | Network pilot (only after a positive Phase 1b) | not started; project closed |

The work was carried out with the help of Claude Code (see Section 11 of the closing report).

## License

MIT, see `LICENSE`.
