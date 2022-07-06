# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 TDoTP.
#
# TDotDat is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""JSON Schemas."""

from invenio_jsonschemas import current_jsonschemas
from invenio_records_rest.schemas import Nested, StrictKeysMixin
from invenio_records_rest.schemas.fields import (
    DateString,
    GenFunction,
    PersistentIdentifier,
    SanitizedUnicode,
)
from marshmallow import fields, missing, validate

from tdotdat.records.api import Record


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
    return record.get("_schema", current_jsonschemas.path_to_url(Record._schema))


class PersonIdsSchemaV1(StrictKeysMixin):
    """Ids schema."""

    source = SanitizedUnicode()
    value = SanitizedUnicode()


class ContributorSchemaV1(StrictKeysMixin):
    """Contributor schema."""

    ids = fields.Nested(PersonIdsSchemaV1, many=True)
    name = SanitizedUnicode(required=True)
    role = SanitizedUnicode()
    affiliations = fields.List(SanitizedUnicode())
    email = fields.Email()


class SoftwareSchemaV1(StrictKeysMixin):
    name = SanitizedUnicode(required=True)
    version = SanitizedUnicode()


class InputsSchemaV1(StrictKeysMixin):
    files = fields.List(SanitizedUnicode)
    temperature = fields.Number()
    temperature_gradient = fields.Number()


class OutputsSchemaV1(StrictKeysMixin):
    files = fields.List(SanitizedUnicode)
    flux = fields.List(fields.Number())
    wavenumber = fields.List(fields.Number())


class MetadataSchemaV1(StrictKeysMixin):
    """Schema for the record metadata."""

    id = PersistentIdentifier()
    title = SanitizedUnicode(required=True, validate=validate.Length(min=3))
    keywords = fields.List(SanitizedUnicode(), many=True)
    publication_date = DateString()
    contributors = Nested(ContributorSchemaV1, many=True, required=True)
    software = Nested(SoftwareSchemaV1)
    inputs = Nested(InputsSchemaV1)
    outputs = Nested(OutputsSchemaV1)
    _schema = GenFunction(
        attribute="$schema",
        data_key="$schema",
        deserialize=schema_from_context,  # to be added only when loading
    )


class RecordSchemaV1(StrictKeysMixin):
    """Record schema."""

    metadata = fields.Nested(MetadataSchemaV1)
    created = fields.Str(dump_only=True)
    revision = fields.Integer(dump_only=True)
    updated = fields.Str(dump_only=True)
    links = fields.Dict(dump_only=True)
    id = PersistentIdentifier()
    files = GenFunction(serialize=files_from_context, deserialize=files_from_context)
