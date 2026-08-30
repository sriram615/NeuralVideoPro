"""
Import & Syntax Verification Test for app.py.

Verifies:
    1. Streamlit app imports without errors or syntax issues.
    2. Essential helper functions format_timestamp, predict_alpha, and get_pipeline are present.
    3. Auto-Alpha prediction logic returns expected (alpha, label) tuples.
"""

from __future__ import annotations

import os

os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    print("=" * 70)
    print("  Streamlit App Imports & Auto-Alpha Verification Test")
    print("=" * 70)

    # 1. Import app module
    import app

    print("[IMPORT] app.py imported successfully ✓")

    # 2. Check helper functions
    assert hasattr(app, "format_timestamp"), "app.py missing format_timestamp function!"
    assert hasattr(app, "get_pipeline"), "app.py missing get_pipeline function!"
    assert hasattr(app, "predict_alpha"), "app.py missing predict_alpha function!"

    # 3. Test timestamp formatter
    formatted = app.format_timestamp(83.0)
    assert formatted == "01:23", f"Expected '01:23', got '{formatted}'"
    print(f"[TEST] format_timestamp(83.0) -> '{formatted}' ✓")

    # 4. Test Auto-Alpha Intent Classification
    alpha_v, label_v = app.predict_alpha("person in suit standing at podium")
    assert alpha_v == 0.8 and label_v == "High Visual Bias", f"Expected (0.8, 'High Visual Bias'), got ({alpha_v}, '{label_v}')"
    print(f"[TEST] predict_alpha('person in suit standing at podium') -> ({alpha_v}, '{label_v}') ✓")

    alpha_a, label_a = app.predict_alpha("speech transcript quote retaliate")
    assert alpha_a == 0.2 and label_a == "High Audio/Speech Bias", f"Expected (0.2, 'High Audio/Speech Bias'), got ({alpha_a}, '{label_a}')"
    print(f"[TEST] predict_alpha('speech transcript quote retaliate') -> ({alpha_a}, '{label_a}') ✓")

    alpha_h, label_h = app.predict_alpha("Obama farewell speech White House podium")
    assert alpha_h == 0.5 and label_h == "Balanced Hybrid", f"Expected (0.5, 'Balanced Hybrid'), got ({alpha_h}, '{label_h}')"
    print(f"[TEST] predict_alpha('Obama farewell speech White House podium') -> ({alpha_h}, '{label_h}') ✓")

    print("\n" + "=" * 70)
    print("  APP IMPORT & AUTO-ALPHA TEST PASSED ✓")
    print("=" * 70)


def test_app_imports() -> None:
    main()


if __name__ == "__main__":
    main()
