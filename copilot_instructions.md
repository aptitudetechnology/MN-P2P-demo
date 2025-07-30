Sure! Here's a clear, step-by-step instruction text you can put in `copilot-instructions.md` or use to prompt GitHub Copilot. It explains the import error and asks it to inspect the source to find and fix the issue:

---

# GitHub Copilot Instructions: Fix ImportError for `db`

## Problem Description

When running `python3 app.py`, the application crashes with:

```
ImportError: cannot import name 'db' from 'models' (unknown location)
```

This means the app tries to import `db` from the `models` package or module, but it cannot find `db` there.

## What to do

1. Inspect the source code to find where `db` (the database instance, likely from `SQLAlchemy`) is defined or instantiated.

2. Common places to check include:

   * `models/__init__.py`
   * `models.py`
   * `extensions.py`
   * `database.py`
   * Or any other module related to database setup

3. Check if the `models` directory has an `__init__.py`. If not, suggest adding it or adjusting the import accordingly.

4. Determine the correct import path for `db` and update `app.py`'s import statement accordingly.

5. Suggest fixes:

   * If `db` is defined in another module, change `from models import db` to `from <correct_module> import db`.
   * If `db` is missing, suggest adding the standard `db = SQLAlchemy()` initialization in an appropriate place.

## Additional Tips

* Look for `db = SQLAlchemy()` or similar patterns.
* Ensure all imports follow Python package/module conventions.
* Explain any changes you make.

---

Would you like me to generate a pull request or a code snippet with the corrected import?
