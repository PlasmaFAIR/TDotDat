from .providers import EquilibriumIdProvider


def equilibrium_pid_minter(record_uuid, data):
    """Mint loan identifiers."""
    assert "id" not in data
    provider = EquilibriumIdProvider.create(
        object_type="rec",
        object_uuid=record_uuid,
    )
    data["id"] = provider.pid.pid_value
    return provider.pid
