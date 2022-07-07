from invenio_pidstore.models import PIDStatus
from invenio_pidstore.providers.recordid import RecordIdProvider


class EquilibriumIdProvider(RecordIdProvider):
    """Author identifier provider."""

    pid_type = "equid"
    """Type of persistent identifier."""

    pid_provider = None
    """Provider name.

    The provider name is not recorded in the PID since the provider does not
    provide any additional features besides creation of record ids.
    """

    default_status = PIDStatus.REGISTERED
    """Record IDs are by default registered immediately."""
