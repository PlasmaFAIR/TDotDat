from invenio_jsonschemas import current_jsonschemas
from invenio_records_rest.schemas import StrictKeysMixin
from invenio_records_rest.schemas.fields import (
    DateString,
    GenFunction,
    PersistentIdentifier,
    SanitizedUnicode,
)
from marshmallow import fields, missing, validate

from tdotdat.equilibrium.api import Equilibrium


def bucket_from_context(_, context):
    """Get the record's bucket from context."""
    record = (context or {}).get("record", {})
    return record.get("_bucket", missing)


def files_from_context(_, context):
    """Get the record's files from context."""
    record = (context or {}).get("record", {})
    return record.get("_files", missing)


def schema_from_context(_, context):
    """Get the record's schema from context."""
    record = (context or {}).get("record", {})
    return record.get("_schema", current_jsonschemas.path_to_url(Equilibrium._schema))


class EquilibriumMetadataSchemaV1(StrictKeysMixin):

    pid = PersistentIdentifier()
    title = SanitizedUnicode(required=True, validate=validate.Length(min=3))
    _schema = GenFunction(
        attribute="$schema",
        data_key="$schema",
        deserialize=schema_from_context,  # to be added only when loading
    )
    elongation = fields.Number()
    q = fields.Number()
    B0 = fields.Number()


class EquilibriumSchemaV1(StrictKeysMixin):
    metadata = fields.Nested(EquilibriumMetadataSchemaV1)
    created = fields.Str(dump_only=True)
    updated = fields.Str(dump_only=True)
    id = PersistentIdentifier()
    files = GenFunction(serialize=files_from_context, deserialize=files_from_context)
