import jsonresolver
from invenio_pidstore.resolver import Resolver
from tdotdat.records.api import Record


# the host corresponds to the config value for the key JSONSCHEMAS_HOST
@jsonresolver.route('/api/resolver/equilibrium/<equid>', host='tdotdat.com')
def record_jsonresolver(equid):
    """Resolve referenced equilibrium."""
    # Setup a resolver to retrieve an equilibrium record given its id
    resolver = Resolver(pid_type='equid', object_type="rec", getter=Record.get_record)
    _, record = resolver.resolve(str(equid))
    # Get rid of bits we don't want
    del record['$schema']
    del record["_bucket"]
    return record
