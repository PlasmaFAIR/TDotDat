from invenio_records_rest.loaders.marshmallow import marshmallow_loader

from ..marshmallow import EquilibriumMetadataSchemaV1

#: JSON loader using Marshmallow for data validation.
json_v1 = marshmallow_loader(EquilibriumMetadataSchemaV1)

__all__ = ("json_v1",)
