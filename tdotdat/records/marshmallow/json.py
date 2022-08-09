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
from marshmallow.fields import List, Number, Boolean

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


class EigenmodeSchemaV1(StrictKeysMixin):
    frequency_norm = Number()
    growth_rate_norm = Number()


class WavevectorSchemaV1(StrictKeysMixin):
    binormal_component_norm = Number()
    eigenmode = List(Nested(EigenmodeSchemaV1))
    poloidal_turns = Number()
    radial_component_norm = Number()


class TagSchemaV1(StrictKeysMixin):
    comment = SanitizedUnicode()
    name = SanitizedUnicode()


class Species_allSchemaV1(StrictKeysMixin):
    beta_reference = Number()
    debye_length_reference = Number()
    shearing_rate_norm = Number()
    velocity_tor_norm = Number()
    zeff = Number()


class SpeciesSchemaV1(StrictKeysMixin):
    charge_norm = Number()
    density_log_gradient_norm = Number()
    density_norm = Number()
    mass_norm = Number()
    temperature_log_gradient_norm = Number()
    temperature_norm = Number()
    velocity_tor_gradient_norm = Number()


class Normalizing_quantitiesSchemaV1(StrictKeysMixin):
    b_field_tor = Number()
    n_e = Number()
    r = Number()
    t_e = Number()


class ModelSchemaV1(StrictKeysMixin):
    include_a_field_parallel = Boolean()
    include_centrifugal_effects = Boolean()
    include_full_curvature_drift = Boolean()
    initial_value_run = Boolean()
    non_linear_run = Boolean()
    time_interval_norm = List(Number())


class Fluxes_integrated_normSchemaV1(StrictKeysMixin):
    particles_a_field_parallel = Number()
    particles_phi_potential = Number()


class Flux_surfaceSchemaV1(StrictKeysMixin):
    b_field_tor_sign = Number()
    elongation = Number()
    ip_sign = Number()
    magnetic_shear_r_minor = Number()
    pressure_gradient_norm = Number()
    q = Number()
    r_minor_norm = Number()
    triangularity_lower = Number()
    triangularity_upper = Number()


class CollisionsSchemaV1(StrictKeysMixin):
    collisionality_norm = List(Number())


class LibrarySchemaV1(StrictKeysMixin):
    commit = SanitizedUnicode()
    name = SanitizedUnicode()
    parameters = SanitizedUnicode()
    repository = SanitizedUnicode()
    version = SanitizedUnicode()


class SoftwareSchemaV1(StrictKeysMixin):
    commit = SanitizedUnicode()
    library = List(Nested(LibrarySchemaV1))
    name = SanitizedUnicode()
    output_flag = List(Boolean())
    parameters = SanitizedUnicode()
    repository = SanitizedUnicode()
    version = SanitizedUnicode()


class GyrokineticsSchemaV1(StrictKeysMixin):
    collisions = Nested(CollisionsSchemaV1)
    flux_surface = Nested(Flux_surfaceSchemaV1)
    fluxes_integrated_norm = List(Nested(Fluxes_integrated_normSchemaV1))
    model = Nested(ModelSchemaV1)
    normalizing_quantities = Nested(Normalizing_quantitiesSchemaV1)
    species = List(Nested(SpeciesSchemaV1))
    species_all = Nested(Species_allSchemaV1)
    tag = List(Nested(TagSchemaV1))
    time = List(Number())
    wavevector = List(Nested(WavevectorSchemaV1))


class InputsSchemaV1(StrictKeysMixin):
    files = fields.List(SanitizedUnicode())
    temperature = fields.Number()
    temperature_gradient = fields.Number()


class OutputsSchemaV1(StrictKeysMixin):
    files = fields.List(SanitizedUnicode())
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
    collisions = Nested(CollisionsSchemaV1)
    flux_surface = Nested(Flux_surfaceSchemaV1)
    fluxes_integrated_norm = List(Nested(Fluxes_integrated_normSchemaV1))
    model = Nested(ModelSchemaV1)
    normalizing_quantities = Nested(Normalizing_quantitiesSchemaV1)
    species = List(Nested(SpeciesSchemaV1))
    species_all = Nested(Species_allSchemaV1)
    tag = List(Nested(TagSchemaV1))
    time = List(Number())
    wavevector = List(Nested(WavevectorSchemaV1))
    converged = Boolean()
    inputs = Nested(InputsSchemaV1)
    outputs = Nested(OutputsSchemaV1)
    _schema = GenFunction(
        attribute="$schema",
        data_key="$schema",
        deserialize=schema_from_context,  # to be added only when loading
    )


class RecordSchemaV1(StrictKeysMixin):
    """Record schema."""

    metadata = Nested(MetadataSchemaV1)
    created = fields.Str(dump_only=True)
    revision = fields.Integer(dump_only=True)
    updated = fields.Str(dump_only=True)
    links = fields.Dict(dump_only=True)
    id = PersistentIdentifier()
    files = GenFunction(serialize=files_from_context, deserialize=files_from_context)
