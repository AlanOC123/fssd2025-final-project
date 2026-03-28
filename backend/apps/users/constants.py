class MembershipVocabulary:
    """Constants representing the various states of a membership.

    This class serves as a central vocabulary for membership lifecycle states
    and groups them into active and inactive categories for easy lookup.
    """

    PENDING = "PENDING_TRAINER_REVIEW"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"
    DISSOLVED_BY_CLIENT = "DISSOLVED_BY_CLIENT"
    DISSOLVED_BY_TRAINER = "DISSOLVED_BY_TRAINER"

    # Sets for logical grouping of states
    ACTIVE_STATES = {PENDING, ACTIVE}
    INACTIVE_STATES = {REJECTED, DISSOLVED_BY_CLIENT, DISSOLVED_BY_TRAINER}
