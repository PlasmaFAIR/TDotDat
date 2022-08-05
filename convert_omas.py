#!/usr/bin/env python3

import argparse
import json
import pathlib
import re
from benedict import benedict


def prune(gk):
    """Remove the keys we're not (currently) interested in"""

    DROP_KEYS_CONTAINING = [
        "b_field_parallel",
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


def to_json_schema(d):
    """Convert OMAS schema to JSON schema"""

    nested = benedict()
    for key, value in d.items():
        path = dotted_name_to_nested_name(key)
        nested[path] = convert_value(value)

    return nested


def convert_value(value):
    """Convert single OMAS schema key to JSON schema key"""

    DATA_TYPES = {
        "STRU": "object",
        "STR_": "string",
        "FLT_": "number",
        "INT_": "boolean",
        "CPX_": "object",
        "cons": "number",
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
    data_type = value["data_type"]
    json_element_type = DATA_TYPES[data_type[:4]]
    is_array = bool(re.search(r"[1-9]+D", data_type)) or data_type.endswith("ARRAY")
    is_object = json_element_type == "object"

    json_type = {"type": "array" if is_array else json_element_type}
    if is_object:
        properties = {}
        if data_type.startswith("CPX"):
            properties["real"] = {"type": "number"}
            properties["imag"] = {"type": "number"}
        else:
            for k, v in value.items():
                if k in IGNORED_COMPONENTS:
                    continue
                properties[k] = convert_value(v)

    if is_array:
        json_type["items"] = {"type": json_element_type}
        if is_object:
            json_type["items"]["properties"] = properties
    elif is_object:
        json_type["properties"] = properties

    if docs := value.get("documentation", None):
        json_type["description"] = docs

    return json_type


def convert_omas_to_json_schema(filename):
    """Read and convert OMAS schema to JSON schema"""
    gk = read_schema(filename)
    prune(gk)
    converted = to_json_schema(to_benedict(gk))
    return json.loads(converted.to_json(sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Convert OMAS schema to JSON schema")
    parser.add_argument("file", help="Filename of OMAS schema")

    args = parser.parse_args()

    print(convert_omas_to_json_schema(args.file))
