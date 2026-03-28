from decimal import Decimal
from math import e

# Mapping of repetitions to the estimated percentage of one-rep max.
# Used for standardizing load distribution across different rep ranges.
LOAD_CHART = {
    1: Decimal("1.00"),
    2: Decimal("0.95"),
    3: Decimal("0.93"),
    4: Decimal("0.90"),
    5: Decimal("0.87"),
    6: Decimal("0.85"),
    7: Decimal("0.83"),
    8: Decimal("0.80"),
    9: Decimal("0.77"),
    10: Decimal("0.75"),
    11: Decimal("0.73"),
    12: Decimal("0.70"),
    13: Decimal("0.67"),
    14: Decimal("0.65"),
    15: Decimal("0.63"),
    16: Decimal("0.60"),
    17: Decimal("0.57"),
    18: Decimal("0.55"),
    19: Decimal("0.53"),
    20: Decimal("0.50"),
}


def epley_one_rep_max(weight, reps):
    """Calculates the estimated 1RM using the Epley formula.

    Args:
        weight: The weight lifted (Decimal).
        reps: The number of repetitions performed (int).

    Returns:
        Decimal: The estimated one-rep max.
    """
    if reps <= 1:
        return weight

    return weight * (1 + Decimal(reps) / Decimal(30))


def brzycki_one_rep_max(weight, reps):
    """Calculates the estimated 1RM using the Brzycki formula.

    Args:
        weight: The weight lifted (Decimal).
        reps: The number of repetitions performed (int).

    Returns:
        Decimal: The estimated one-rep max.
    """
    if reps <= 1:
        return weight

    return weight * (Decimal(36) / (Decimal(37) - Decimal(reps)))


def lander_one_rep_max(weight, reps):
    """Calculates the estimated 1RM using the McGlothin (Lander) formula.

    Args:
        weight: The weight lifted (Decimal).
        reps: The number of repetitions performed (int).

    Returns:
        Decimal: The estimated one-rep max.
    """
    if reps <= 1:
        return weight

    return (Decimal(100) * weight) / (
        Decimal("101.3") - Decimal("2.67123") * Decimal(reps)
    )


def lombardi_one_rep_max(weight, reps):
    """Calculates the estimated 1RM using the Lombardi formula.

    Args:
        weight: The weight lifted (Decimal).
        reps: The number of repetitions performed (int).

    Returns:
        Decimal: The estimated one-rep max.
    """
    if reps <= 1:
        return weight

    return weight * Decimal(str(reps**0.1))


def mayhew_one_rep_max(weight, reps):
    """Calculates the estimated 1RM using the Mayhew et al. formula.

    Args:
        weight: The weight lifted (Decimal).
        reps: The number of repetitions performed (int).

    Returns:
        Decimal: The estimated one-rep max.
    """
    if reps <= 1:
        return weight
    return (Decimal(100) * weight) / (
        Decimal("52.2") + Decimal(str(41.9 * e ** (-0.055 * reps)))
    )


def o_conner_one_rep_max(weight, reps):
    """Calculates the estimated 1RM using the O'Conner et al. formula.

    Args:
        weight: The weight lifted (Decimal).
        reps: The number of repetitions performed (int).

    Returns:
        Decimal: The estimated one-rep max.
    """
    if reps <= 1:
        return weight

    return weight * (1 + Decimal("0.025") * Decimal(reps))


def wathan_one_rep_max(weight, reps):
    """Calculates the estimated 1RM using the Wathan formula.

    Args:
        weight: The weight lifted (Decimal).
        reps: The number of repetitions performed (int).

    Returns:
        Decimal: The estimated one-rep max.
    """
    if reps <= 1:
        return weight
    return (Decimal(100) * weight) / (
        Decimal("48.8") + Decimal(str(53.8 * e ** (-0.075 * reps)))
    )


def weight_at_reps(one_rep_max, reps):
    """Calculates the predicted weight for a given number of repetitions.

    Uses the LOAD_CHART to find the percentage of 1RM corresponding to the
    target reps. If the exact rep count is not in the chart, it uses the
    nearest available value.

    Args:
        one_rep_max: The estimated 1RM of the user (Decimal).
        reps: The target number of repetitions (int).

    Returns:
        Decimal: The estimated weight to be used for the given reps.
    """
    if reps in LOAD_CHART:
        return one_rep_max * LOAD_CHART[reps]

    nearest = min(LOAD_CHART.keys(), key=lambda r: abs(r - reps))

    return one_rep_max * LOAD_CHART[nearest]
