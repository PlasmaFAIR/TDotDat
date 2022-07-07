from invenio_pidstore.fetchers import FetchedPID


def equilibrium_pid_fetcher(record_uuid, data):
    return FetchedPID(provider=None, pid_type="equid", pid_value=str(data["id"]))
