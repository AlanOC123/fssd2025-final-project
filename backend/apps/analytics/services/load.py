"""Service module for calculating biomechanical load distribution.

This module provides utility functions to convert raw lifting data (reps and weight)
into distributed loads across anatomical joints and individual muscles based on
impact factors and range of motion.
"""

from decimal import Decimal


def calculate_raw_set_load(reps, weight):
    """Calculates the total volume for a single set.

    Args:
        reps: The number of repetitions completed.
        weight: The weight used for the repetitions (Decimal).

    Returns:
        Decimal: The total weight volume for the set.
    """
    return Decimal(reps) * weight


def calculate_session_load(set_records):
    """Calculates the total volume for an entire exercise session.

    Sums the raw load of all sets that were not explicitly marked as skipped.

    Args:
        set_records: An iterable of set record objects containing reps and weight.

    Returns:
        Decimal: The total volume for the session.
    """
    return sum(
        calculate_raw_set_load(s.reps_completed, s.weight_completed)
        for s in set_records
        if not s.is_skipped
    )


def calculate_joint_load(raw_set_load: Decimal, joint_contributions):
    """Distributes raw set load across joint actions.

    Uses the impact factor of the joint's range of motion (ROM) to determine
    how much of the total set load is applied to specific joint actions.

    Args:
        raw_set_load: The total volume of the set (Decimal).
        joint_contributions: A list of objects linking the movement to joint actions
            via a range of motion impact factor.

    Returns:
        list[dict]: A list of dictionaries containing the 'joint_action' instance
            and the calculated 'load' for that action.
    """
    return [
        {
            "joint_action": jc.joint_action,
            "load": raw_set_load * jc.joint_range_of_motion.impact_factor,
        }
        for jc in joint_contributions
    ]


def calculate_muscle_load(joint_loads: list[dict]):
    """Distributes joint-level load across individual muscles.

    Calculates the specific load impact on muscles based on their involvement
    factor and functional role (e.g., Agonist, Synergist) in a joint action.

    Args:
        joint_loads: A list of dictionaries containing 'joint_action' and 'load'.

    Returns:
        list[dict]: A list of dictionaries containing the 'muscle' instance,
            the 'role' (string code), and the calculated 'load' for that muscle.
    """
    results = []
    for entry in joint_loads:
        joint_action = entry["joint_action"]
        joint_load = entry["load"]

        # Prefetching related muscle and role data for performance
        for involvement in joint_action.muscles.select_related("muscle", "role").all():
            results.append(
                {
                    "muscle": involvement.muscle,
                    "role": involvement.role.code,
                    "load": joint_load * involvement.impact_factor,
                }
            )
    return results
