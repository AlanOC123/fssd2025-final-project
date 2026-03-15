from decimal import Decimal


def calculate_raw_set_load(reps, weight):
    return Decimal(reps) * weight


def calculate_session_load(set_records):
    return sum(
        calculate_raw_set_load(s.reps_completed, s.weight_completed)
        for s in set_records
        if not s.is_skipped
    )


def calculate_joint_load(raw_set_load: Decimal, joint_contributions):
    """
    Distributes raw set load across joint actions using ROM impact factor.
    Returns a list of {joint_action, load} dicts.
    """
    return [
        {
            "joint_action": jc.joint_action,
            "load": raw_set_load * jc.joint_range_of_motion.impact_factor,
        }
        for jc in joint_contributions
    ]


def calculate_muscle_load(joint_loads: list[dict]):
    """
    Further distributes joint load across muscles using MuscleInvolvement impact_factor.
    Includes role so callers can filter by AGONIST, SYNERGIST etc.
    """
    results = []
    for entry in joint_loads:
        joint_action = entry["joint_action"]
        joint_load = entry["load"]
        for involvement in joint_action.muscles.select_related("muscle", "role").all():
            results.append(
                {
                    "muscle": involvement.muscle,
                    "role": involvement.role.code,
                    "load": joint_load * involvement.impact_factor,
                }
            )
    return results
