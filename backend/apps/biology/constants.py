class PlaneOfMotionVocabulary:
    """Constants for anatomical planes of motion.

    Defines the standard planes used to describe human movement and
    anatomical positioning.
    """

    SAGITTAL = "SAGITTAL"
    FRONTAL = "FRONTAL"
    TRANSVERSE = "TRANSVERSE"


class AnatomicalDirectionVocabulary:
    """Constants for anatomical directions and positions.

    Provides a standardized vocabulary for describing the location of
    structures relative to the body or other structures.
    """

    ANTERIOR = "ANTERIOR"
    POSTERIOR = "POSTERIOR"
    LATERAL = "LATERAL"
    MEDIAL = "MEDIAL"
    SUPERIOR = "SUPERIOR"
    INFERIOR = "INFERIOR"


class MovementPatternVocabulary:
    """Constants for joint movement patterns.

    Contains standard terminology for describing specific angular
    movements of the human skeletal system.
    """

    FLEXION = "FLEXION"
    EXTENSION = "EXTENSION"
    ABDUCTION = "ABDUCTION"
    ADDUCTION = "ADDUCTION"
    INTERNAL_ROTATION = "INTERNAL_ROTATION"
    EXTERNAL_ROTATION = "EXTERNAL_ROTATION"
    HORIZONTAL_ADDUCTION = "HORIZONTAL_ADDUCTION"
    HORIZONTAL_ABDUCTION = "HORIZONTAL_ABDUCTION"
    DORSIFLEXION = "DORSIFLEXION"
    PLANTARFLEXION = "PLANTARFLEXION"
    ELEVATION = "ELEVATION"
    DEPRESSION = "DEPRESSION"
    PROTRACTION = "PROTRACTION"
    RETRACTION = "RETRACTION"


class MuscleRoleVocabulary:
    """Constants for functional muscle classifications.

    Defines roles muscles play during a specific movement or joint action.
    """

    AGONIST = "AGONIST"
    ANTAGONIST = "ANTAGONIST"
    SYNERGIST = "SYNERGIST"
    FIXATOR = "FIXATOR"


class JointVocabulary:
    """Constants for major anatomical joints.

    Standardizes the identifiers for primary joints involved in movement
    analysis and exercise programming.
    """

    SHOULDER = "SHOULDER"
    ELBOW = "ELBOW"
    SPINE = "SPINE"
    HIP = "HIP"
    KNEE = "KNEE"
    ANKLE = "ANKLE"
    SCAPULA = "SCAPULA"


class MuscleGroupVocabulary:
    """Constants for major muscle groups.

    Categorizes specific muscles into broader functional or anatomical
    groups for training and analysis purposes.
    """

    CHEST = "CHEST"
    SHOULDER = "SHOULDER"
    TRICEPS = "TRICEPS"

    BACK = "BACK"
    BICEPS = "BICEPS"
    UPPER_ARM = "UPPER_ARM"
    LOWER_ARM = "LOWER_ARM"
    FOREARM = "FOREARM"

    CORE = "CORE"

    GLUTES = "GLUTES"
    QUADRICEPS = "QUADRICEPS"
    HAMSTRINGS = "HAMSTRINGS"
    CALVES = "CALVES"
    HIP_FLEXORS = "HIP_FLEXORS"
