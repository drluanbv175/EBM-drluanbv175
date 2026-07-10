"""
Bo kiem thu mau cho mot clinical calculator.
Nguyen tac: moi NGUONG va moi BIEN (boundary) phai co test rieng.
Vi du minh hoa: phan loai BMI (thay bang logic lam sang thuc te cua ban,
va ghi ro nguon cua tung nguong trong comment).
"""

# Nguon nguong: WHO BMI classification [nguon: WHO, 2024] - thay bang nguon thuc te.
UNDERWEIGHT_MAX = 18.5
NORMAL_MAX = 25.0
OVERWEIGHT_MAX = 30.0


def classify_bmi(bmi: float) -> str:
    if bmi < 0:
        raise ValueError("BMI khong the am")
    if bmi < UNDERWEIGHT_MAX:
        return "underweight"
    if bmi < NORMAL_MAX:
        return "normal"
    if bmi < OVERWEIGHT_MAX:
        return "overweight"
    return "obese"


# --- Tests: chay bang `pytest scripts/test_clinical_calculator.py` ---

def test_below_underweight_boundary():
    assert classify_bmi(18.4) == "underweight"

def test_at_underweight_boundary():
    assert classify_bmi(18.5) == "normal"

def test_at_normal_upper_boundary():
    assert classify_bmi(24.9) == "normal"
    assert classify_bmi(25.0) == "overweight"

def test_at_overweight_upper_boundary():
    assert classify_bmi(29.9) == "overweight"
    assert classify_bmi(30.0) == "obese"

def test_rejects_negative():
    import pytest
    with pytest.raises(ValueError):
        classify_bmi(-1)
