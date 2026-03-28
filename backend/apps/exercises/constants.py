class ExercisePhaseVocabulary:
    """Vocabulary for different phases of an exercise.

    Attributes:
        CONCENTRIC (str): The phase of muscle contraction where the muscle shortens.
        ECCENTRIC (str): The phase of muscle contraction where the muscle lengthens.
        ISOMETRIC (str): The phase of muscle contraction where the muscle length
            remains constant.
    """

    CONCENTRIC = "CONCENTRIC"
    ECCENTRIC = "ECCENTRIC"
    ISOMETRIC = "ISOMETRIC"


class JointRangeOfMotionVocabulary:
    """Vocabulary for describing the range of motion of a joint.

    Attributes:
        FULL (str): Indicates the joint is moving through its complete available
            range of motion.
        PARTIAL (str): Indicates the joint is moving through only a portion of its
            available range of motion.
    """

    FULL = "FULL"
    PARTIAL = "PARTIAL"
