import uuid

from invenio_db import db
from invenio_jsonschemas import current_jsonschemas
from invenio_indexer.api import RecordIndexer
from invenio_pidstore import current_pidstore
from invenio_records_files.api import Record as FilesRecord


class Equilibrium(FilesRecord):
    _schema = "equilibrium/equilibrium-v1.0.0.json"

    @classmethod
    def create(cls, data, id_=None, **kwargs):
        """Create Equilibrium record."""
        data["$schema"] = current_jsonschemas.path_to_url(cls._schema)
        return super().create(data, id_=id_, **kwargs)


def create_equilibrium(data):
    """Create an equilibrium

    :param dict data: The record data.
    """
    with db.session.begin_nested():
        # create uuid
        equ_uuid = uuid.uuid4()
        # create PID
        current_pidstore.minters["equid"](equ_uuid, data)
        # create equilibrium
        created_equilibrium = Equilibrium.create(data, id_=equ_uuid)
        # index the equilibrium
        RecordIndexer().index(created_equilibrium)
    db.session.commit()
