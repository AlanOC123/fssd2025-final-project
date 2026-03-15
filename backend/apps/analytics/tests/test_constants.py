from decimal import Decimal

import pytest

from apps.analytics.constants import (
    LOAD_CHART,
    brzycki_one_rep_max,
    epley_one_rep_max,
    lander_one_rep_max,
    lombardi_one_rep_max,
    mayhew_one_rep_max,
    o_conner_one_rep_max,
    wathan_one_rep_max,
    weight_at_reps,
)


class TestEpleyFormula:

    def test_single_rep_returns_weight_unchanged(self):
        assert epley_one_rep_max(Decimal("100"), 1) == Decimal("100")

    def test_known_value(self):
        # 60kg × (1 + 10/30) = 60 × 1.333... = 80
        result = epley_one_rep_max(Decimal("60"), 10)
        assert result == pytest.approx(Decimal("80"), rel=Decimal("0.01"))

    def test_higher_reps_produces_higher_1rm(self):
        lower = epley_one_rep_max(Decimal("100"), 5)
        higher = epley_one_rep_max(Decimal("100"), 10)
        assert higher > lower

    def test_returns_decimal(self):
        result = epley_one_rep_max(Decimal("80"), 8)
        assert isinstance(result, Decimal)


class TestBrzyckiFormula:

    def test_single_rep_returns_weight_unchanged(self):
        assert brzycki_one_rep_max(Decimal("100"), 1) == Decimal("100")

    def test_known_value(self):
        # 100kg × (36 / (37 - 10)) = 100 × 36/27 = 133.33
        result = brzycki_one_rep_max(Decimal("100"), 10)
        assert float(result) == pytest.approx(133.33, rel=0.01)

    def test_returns_decimal(self):
        assert isinstance(brzycki_one_rep_max(Decimal("80"), 5), Decimal)


class TestLanderFormula:

    def test_single_rep_returns_weight_unchanged(self):
        assert lander_one_rep_max(Decimal("100"), 1) == Decimal("100")

    def test_returns_decimal(self):
        assert isinstance(lander_one_rep_max(Decimal("80"), 5), Decimal)

    def test_positive_result(self):
        result = lander_one_rep_max(Decimal("60"), 10)
        assert result > Decimal("60")


class TestLombardiFormula:

    def test_single_rep_returns_weight_unchanged(self):
        assert lombardi_one_rep_max(Decimal("100"), 1) == Decimal("100")

    def test_returns_decimal(self):
        assert isinstance(lombardi_one_rep_max(Decimal("80"), 5), Decimal)

    def test_positive_result(self):
        result = lombardi_one_rep_max(Decimal("60"), 10)
        assert result > Decimal("0")


class TestMayhewFormula:

    def test_single_rep_returns_weight_unchanged(self):
        assert mayhew_one_rep_max(Decimal("100"), 1) == Decimal("100")

    def test_returns_decimal(self):
        assert isinstance(mayhew_one_rep_max(Decimal("80"), 8), Decimal)

    def test_positive_result(self):
        result = mayhew_one_rep_max(Decimal("60"), 10)
        assert result > Decimal("60")


class TestOConnerFormula:

    def test_single_rep_returns_weight_unchanged(self):
        assert o_conner_one_rep_max(Decimal("100"), 1) == Decimal("100")

    def test_known_value(self):
        # 100 × (1 + 0.025 × 10) = 100 × 1.25 = 125
        result = o_conner_one_rep_max(Decimal("100"), 10)
        assert result == Decimal("125")

    def test_returns_decimal(self):
        assert isinstance(o_conner_one_rep_max(Decimal("80"), 5), Decimal)


class TestWathanFormula:

    def test_single_rep_returns_weight_unchanged(self):
        assert wathan_one_rep_max(Decimal("100"), 1) == Decimal("100")

    def test_returns_decimal(self):
        assert isinstance(wathan_one_rep_max(Decimal("80"), 8), Decimal)

    def test_positive_result(self):
        result = wathan_one_rep_max(Decimal("60"), 10)
        assert result > Decimal("60")


class TestWeightAtReps:

    def test_exact_rep_count_in_chart(self):
        # 1RM of 100kg at 10 reps = 100 × 0.75 = 75kg
        result = weight_at_reps(Decimal("100"), 10)
        assert result == Decimal("75.00")

    def test_exact_rep_count_6rm(self):
        # 80kg 1RM at 6 reps = 80 × 0.85 = 68kg
        result = weight_at_reps(Decimal("80"), 6)
        assert result == Decimal("68.00")

    def test_exact_rep_count_12rm(self):
        # 80kg 1RM at 12 reps = 80 × 0.70 = 56kg
        result = weight_at_reps(Decimal("80"), 12)
        assert result == Decimal("56.00")

    def test_interpolates_to_nearest_for_unlisted_rep_count(self):
        # Rep count 13 not in original NSCA chart — should map to nearest (12 or 13)
        result = weight_at_reps(Decimal("100"), 13)
        assert result > Decimal("0")

    def test_floor_less_than_ceiling_for_rep_range(self):
        one_rm = Decimal("100")
        floor = weight_at_reps(one_rm, 12)  # max reps → lower weight
        ceiling = weight_at_reps(one_rm, 6)  # min reps → higher weight
        assert floor < ceiling

    def test_load_chart_covers_standard_hypertrophy_range(self):
        for rep in range(6, 13):
            assert rep in LOAD_CHART
