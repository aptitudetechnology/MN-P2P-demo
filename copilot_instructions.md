Certainly! Here's a **Copilot instruction block** that focuses on gathering more information without suggesting explicit fixes:

---

# GitHub Copilot Instructions: Gather Information About ImportError in `models`

## Context

The application fails with the following error:

```
ImportError: cannot import name 'Compound' from 'models' (unknown location)
```

This occurs during the import statement:

```python
from models import Compound, BiochemicalGroup, TherapeuticArea, Disease, Study, db
```

## Task

Please inspect the codebase and collect the following information to help diagnose the issue:

1. Does the `models` directory exist, and does it include an `__init__.py` file?
2. Are the following classes defined anywhere in the `models` package?

   * `Compound`
   * `BiochemicalGroup`
   * `TherapeuticArea`
   * `Disease`
   * `Study`
3. In which files are each of these classes defined?
4. Is the `db` instance defined or imported in `models`, or is it defined elsewhere (such as in `extensions.py`)?
5. Are there any circular import issues that might prevent successful loading of model classes?
6. What are the exact relative or absolute import paths used within the `models` package?

## Output

Provide:

* A list of model classes and the file in which each one is defined.
* Confirmation of whether `__init__.py` exists and what it contains.
* Where `db` is defined and whether it's accessible from the `models` package.

Do not suggest changes or fixes at this stage—just gather and summarize this information.

---

Let me know when you're ready to move to the next step (analysis or fix).
