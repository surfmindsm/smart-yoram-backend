"""Suppress bcrypt warnings for passlib."""

import warnings
import sys

# Suppress the specific bcrypt warning
warnings.filterwarnings("ignore", message=".*error reading bcrypt version.*")

# Also suppress at the module level
if not sys.warnoptions:
    warnings.simplefilter("ignore")
    import os

    os.environ["PYTHONWARNINGS"] = "ignore"
