#!/usr/bin/env python3

import argparse
import json
import pathlib
import re
import textwrap
from benedict import benedict


def prune(gk):
    """Remove the keys we're not (currently) interested in"""

    DROP_KEYS_CONTAINING = [
        "collisions_",
        "dr_minor_norm",
        "energy_",
        "error",
        "fluxes_moments",
        "fluxes_norm_particle",
        "growth_rate_tolerance",
        "ids_properties",
        "moments_norm_gyrocenter",
        "moments_norm_particle",
        "momentum_tor",
        "perturbed_norm",
        "perturbed_parity",
        "perturbed_weight",
        "poloidal_angle",
        "shape_coefficients",
        "time_norm",
    ]

    def drop_key(key):
        return any([bad in key for bad in DROP_KEYS_CONTAINING])

    for key in list(filter(drop_key, gk)):
        del gk[key]

    return arbitrary_fixes(gk)


def arbitrary_fixes(data):
    """Apply some one-off fixes"""

    # All other `INT_` data_types are really booleans, except
    # poloidal_turns, which is really an integer.  Unfortunately, JSON
    # schema's native types only have "number" and not any
    # float/integer distinction
    data["gyrokinetics.wavevector[:].poloidal_turns"]["data_type"] = "FLT_0D"

    # output_flag

    return data


def read_schema(filename: pathlib.Path) -> dict:
    """Read the OMAS gyrokinetics, and drop some of the unnecessary keys"""

    with open(filename) as f:
        gk = json.load(f)

    del gk["gyrokinetics"]

    return gk


def to_benedict(data):
    """Convert data to benedict, normalising any "array" keys"""

    result = benedict()
    for k, v in data.items():
        result[k.replace("[:]", "")] = v
    return result["gyrokinetics"]


def dotted_name_to_nested_name(dotted):
    """Convert flat dotted name to array of keys appropriate for JSON schema"""

    parts = dotted.split(".")

    result = []
    for part in parts:
        if part.endswith("[:]"):
            result.extend([part.replace("[:]", ""), "items"])
        else:
            result.append(part)
    return result


def to_json_schema(d, mapping=False):
    """Convert OMAS schema to JSON schema"""

    nested = benedict()
    for key, value in d.items():
        path = dotted_name_to_nested_name(key)
        nested[path] = convert_value(value, mapping)

    return nested


def to_elasticsearch(d):
    """Convert OMAS schema to elasticsearch JSON schema"""
    return to_json_schema(d, mapping=True)


def convert_value(value, mapping):
    """Convert single OMAS schema key to JSON schema key"""

    DATA_TYPES = {
        "STRU": "object",
        "STR_": "string",
        "FLT_": "number",
        "INT_": "boolean",
        "CPX_": "object",
        "cons": "number",
    }
    MAPPING_DATA_TYPES = {
        "STRU": "object",
        "STR_": "keyword",
        "FLT_": "double",
        "INT_": "boolean",
        "CPX_": "object",
        "cons": "integer",
    }
    IGNORED_COMPONENTS = [
        "coordinates",
        "data_type",
        "documentation",
        "full_path",
        "lifecycle_status",
        "lifecycle_version",
        "maxoccur",
        "structure_reference",
        "type",
    ]
    if mapping:
        IGNORED_COMPONENTS.append("documentation")
    data_type = value["data_type"]
    json_element_type = (MAPPING_DATA_TYPES if mapping else DATA_TYPES)[data_type[:4]]
    is_array = bool(re.search(r"[1-9]+D", data_type)) or data_type.endswith("ARRAY")
    is_object = json_element_type == "object"

    json_type = {"type": "array" if (is_array and not mapping) else json_element_type}
    if is_object:
        properties = {}
        if data_type.startswith("CPX"):
            properties["real"] = {"type": "number"}
            properties["imag"] = {"type": "number"}
        else:
            for k, v in value.items():
                if k in IGNORED_COMPONENTS:
                    continue
                properties[k] = convert_value(v, mapping)

    if is_array and not mapping:
        json_type["items"] = {"type": json_element_type}
        if is_object:
            json_type["items"]["properties"] = properties
    elif is_object:
        json_type["properties"] = properties

    if (docs := value.get("documentation", None)) and not mapping:
        json_type["description"] = docs

    return json_type


def omas_to_json_schema(filename, mapping=False):
    """Read and convert OMAS schema to JSON schema"""
    gk = read_schema(filename)
    prune(gk)
    converted = to_json_schema(to_benedict(gk), mapping)
    return json.loads(converted.to_json(sort_keys=True))


def omas_to_elasticsearch_schema(filename):
    return omas_to_json_schema(filename, mapping=True)


def json_to_marshmallow(data):
    """Convert JSON schema to set of marshmallow validator classes"""

    MARSHMALLOW_TYPES = {
        "number": "Number",
        "string": "SanitizedUnicode",
        "boolean": "Boolean",
        "array": "List",
    }

    def convert_marshmallow(key, value, other_classes=None):
        """Convert a nested dict to equivalent marshmallow types

        Returns a tuple of dicts:
        - the first describes the attributes of the current value
        - the second is an accumulator of any nested classes
        """
        if other_classes is None:
            other_classes = {}

        try:
            type_ = value["type"]
        except KeyError:
            breakpoint()

        if type_ == "object":
            other_classes[key] = {}
            for k, v in value["properties"].items():
                item, others = convert_marshmallow(k, v, other_classes)
                other_classes[key].update(item)
                other_classes.update(others)

            return {key: f"Nested({key.capitalize()}SchemaV1)"}, other_classes

        if type_ == "array":
            item, others = convert_marshmallow(key, value["items"], other_classes)
            other_classes.update(others)

            return {key: f"List({item[key]})"}, other_classes

        marsh_type = MARSHMALLOW_TYPES[type_]
        return {key: f"{marsh_type}()"}, other_classes

    def create_class(name, body):
        """Create the string of the code describing a class defined by a dict of attributes"""
        body_str = textwrap.indent(
            "\n".join(f"{name} = {type_}" for name, type_ in body.items()), " " * 4
        )

        return textwrap.dedent(
            "\n".join(
                [f"class {name.capitalize()}SchemaV1(StrictKeysMixin):"] + [body_str]
            )
        )

    # The passed in data only describes its attributes and not itself,
    # so we need to wrap it up as if it were an object itself
    _, other_classes = convert_marshmallow(
        "gyrokinetics", {"type": "object", "properties": data}
    )
    return "\n\n".join(
        create_class(name, body) for name, body in reversed(other_classes.items())
    )


def json_to_dataclasses(data):
    """Convert JSON schema to set of marshmallow validator classes"""

    PYTHON_TYPES = {
        "number": "float",
        "string": "str",
        "boolean": "bool",
        "array": "list",
    }

    def convert_python(key, value, other_classes=None):
        """Convert a nested dict to equivalent marshmallow types

        Returns a tuple of dicts:
        - the first describes the attributes of the current value
        - the second is an accumulator of any nested classes
        """
        if other_classes is None:
            other_classes = {}

        try:
            type_ = value["type"]
        except KeyError:
            breakpoint()

        if type_ == "object":
            other_classes[key] = {}
            for k, v in value["properties"].items():
                item, others = convert_python(k, v, other_classes)
                other_classes[key].update(item)
                other_classes.update(others)

            return {key: key.capitalize()}, other_classes

        if type_ == "array":
            item, others = convert_python(key, value["items"], other_classes)
            other_classes.update(others)

            return {key: f"List[{item[key]}]"}, other_classes

        marsh_type = PYTHON_TYPES[type_]
        return {key: marsh_type}, other_classes

    def create_class(name, body):
        """Create the string of the code describing a class defined by a dict of attributes"""
        body_str = textwrap.indent(
            "\n".join(
                f"{name}: Optional[{type_}] = None" for name, type_ in body.items()
            ),
            " " * 4,
        )

        return textwrap.dedent(
            "\n".join([f"@dataclass\nclass {name.capitalize()}:"] + [body_str])
        )

    # The passed in data only describes its attributes and not itself,
    # so we need to wrap it up as if it were an object itself
    _, other_classes = convert_python(
        "gyrokinetics", {"type": "object", "properties": data}
    )
    return "\n\n".join(
        create_class(name, body) for name, body in reversed(other_classes.items())
    )


def omas_to_marshmallow(filename):
    data = omas_to_json_schema(filename)
    return json_to_marshmallow(data)


def omas_to_dataclasses(filename):
    data = omas_to_json_schema(filename)
    return json_to_dataclasses(data)


METHODS = {
    "jsonschema": lambda filename: json.dumps(omas_to_json_schema(filename)),
    "elasticsearch": lambda filename: json.dumps(
        omas_to_elasticsearch_schema(filename)
    ),
    "marshmallow": omas_to_marshmallow,
    "dataclasses": omas_to_dataclasses,
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Convert OMAS schema to JSON schema")
    parser.add_argument("filename", help="Filename of OMAS schema")
    parser.add_argument("to", choices=METHODS.keys())

    args = parser.parse_args()

    print(METHODS[args.to](args.filename))
