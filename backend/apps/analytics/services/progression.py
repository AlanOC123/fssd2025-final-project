from decimal import ROUND_HALF_UP, Decimal

from apps.analytics.constants import weight_at_reps
from apps.analytics.services.one_rep_max import (
    get_last_session_load_for_exercise,
    get_program_1rm_for_exercise,
)


def get_next_session_recommendation(program, exercise):
    membership = program.trainer_client_membership

    if not membership:
        return None

    client_profile = membership.client
    experience_level = program.experience_level
    training_goal = program.training_goal

    cap = experience_level.progression_cap_percent
    rep_min = training_goal.rep_range_min
    rep_max = training_goal.rep_range_max

    if cap is None or rep_min is None or rep_max is None:
        return None

    one_rm = get_program_1rm_for_exercise(program, exercise)
    if one_rm is None:
        return None

    last_load = get_last_session_load_for_exercise(program, exercise)
    target_load = last_load * (1 + cap) if last_load > 0 else None

    weight_floor = weight_at_reps(one_rm, rep_max).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    weight_ceiling = weight_at_reps(one_rm, rep_min).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    return {
        "exercise": exercise,
        "one_rep_max": one_rm.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        "last_session_load": last_load,
        "target_load": target_load,
        "rep_range_min": rep_min,
        "rep_range_max": rep_max,
        "weight_floor": weight_floor,
        "weight_ceiling": weight_ceiling,
        "progression_cap_percent": cap,
    }
