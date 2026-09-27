# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project overview

A single-page calculator web app built with [Streamlit](https://streamlit.io). It performs basic arithmetic (addition, subtraction, multiplication, division) on two numbers, styled with a "3D / cosmic" theme.

## Layout

- `app.py` — the entire Streamlit app: page config, CSS loading, Three.js background embed, calculator UI and calculation logic.
- `assets/theme.css` — custom styles injected via `st.markdown(..., unsafe_allow_html=True)`.
- `assets/threejs-background.js` — animated Three.js background canvas.
- `requirements.txt` — Python dependencies (`streamlit`, `streamlit-extras`, `pyweb3d`).

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Run from the repository root: `app.py` opens `assets/theme.css` with a relative path.

## Conventions

- Keep the app in `app.py` unless it grows enough to justify splitting into modules.
- Put styling in `assets/theme.css` rather than inline in Python strings where possible.
- Handle user-input errors (e.g. division by zero) gracefully with `st.error` instead of letting exceptions surface.
- There is no test suite or linter configured yet.

## Deployment

Intended for deployment on Streamlit Community Cloud, which uses `app.py` and `requirements.txt` from the repo root.

## Sub-project: 01-Smart-File-Organizer

`01-Smart-File-Organizer/` is a separate, standalone learning project (a Python file organizer, standard library only), unrelated to the calculator. See its `README.md`.

- Run: `python3 01-Smart-File-Organizer/scripts/organizer.py [--dry-run]`
- Test: `python3 01-Smart-File-Organizer/scripts/test_organizer.py`
- The user is a beginner learning Claude Code: explain steps, keep code simple, never delete user files.
