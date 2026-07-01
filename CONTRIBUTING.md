# Contributing

## Commit convention

Use concise, descriptive commit messages in the format:

```text
type(scope): short description
```

Examples:
- `fix(ci): exclude test dir from bandit scan`
- `feat(applications): add resume upload validation`

## Workflow

1. Make small, focused changes.
2. Run the relevant checks locally before committing.
3. Keep commits single-purpose and easy to review.
4. Do not rewrite existing history.
5. Follow the commit message convention above.

## Local checks

This repository uses pre-commit to run:
- `black`
- `flake8`
- `bandit` (excluding `./tests`, `./venv`, and `./migrations`)

Install the hooks once with:

```bash
pre-commit install
```
