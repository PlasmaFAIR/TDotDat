#!/usr/bin/env python3

import argparse
import pathlib
import requests
import json
from urllib.parse import urljoin

import pyrokinetics


def read(filename: pathlib.Path) -> pyrokinetics.Pyro:
    pyro = pyrokinetics.Pyro(gk_file=filename)
    pyro.load_gk_output()

    return pyro


def convert_to_omas(pyro):

    geometry = pyro.local_geometry
    species_list = [pyro.local_species[name] for name in pyro.local_species.names]

    species_data = [
        {
            "charge_norm": species.z,
            "mass_norm": species.mass,
            "temperature_norm": species.temp,
            "temperature_log_gradient_norm": species.a_lt,
            "density_norm": species.dens,
            "density_log_gradient_norm": species.a_ln,
            "velocity_tor_gradient_norm": species.a_lv,
        }
        for species in species_list
    ]

    data = {
        "software": {"name": pyro.gk_code},
        "wavevector": [],
        "flux_surface": {
            "elongation": geometry.kappa,
            "magnetic_shear_r_minor": geometry.shat,
            "q": geometry.q,
            "triangularity_lower": geometry.delta,
            "triangularity_upper": geometry.delta,
            "r_minor_norm": geometry.rho,
        },
        "species": species_data,
        "model": {
            "non_linear_run": pyro.numerics.nonlinear,
        },
    }

    for kx in range(len(pyro.gk_output.kx)):
        for ky in range(len(pyro.gk_output.ky)):
            point = pyro.gk_output.isel(time=-1, kx=kx, ky=ky)
            data["wavevector"].append(
                dict(
                    radial_component_norm=point.kx.data[()],
                    binormal_component_norm=point.ky.data[()],
                    eigenmode=[
                        dict(
                            frequency_norm=point.mode_frequency.data[()],
                            growth_rate_norm=point.growth_rate.data[()],
                        )
                    ],
                )
            )

    return data


def upload(
    filename, data, server="https://localhost:5000", endpoint="api/records", token=None
):

    url = urljoin(server, endpoint)
    verify = "localhost" not in server
    header = {"Authorization": f"Bearer {token}"} if token else {}

    r = requests.post(url, json=data, verify=verify, headers=header)

    if not r.ok:
        raise RuntimeError(
            f"Server error on initial upload ({r.status_code}): {r.json()}"
        )

    result_json = r.json()

    with open(filename) as f:
        new_id = r.json()["id"]
        file_url = f"{url}/{new_id}/files/{filename.name}"
        r = requests.put(file_url, data=f, verify=verify, headers=header)

    if not r.ok:
        raise RuntimeError(f"Server error on file upload ({r.status_code}): {r.json()}")

    result_json["files"] = r.json()
    return result_json


def run():
    parser = argparse.ArgumentParser("Upload simulation to TDoTDat")
    parser.add_argument("filename", help="Name of input file", type=pathlib.Path)
    parser.add_argument(
        "--contributors",
        default=None,
        nargs="*",
        help="Names of contributors, default is file owner",
    )
    parser.add_argument(
        "--title",
        default=None,
        type=str,
        help="Title of simulation, default is input file name",
    )
    parser.add_argument(
        "--unconverged", action="store_true", help="Is the simulation NOT converged?"
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Don't print received result"
    )
    parser.add_argument(
        "--server", help="URL of TDotDat server", default="https://tdotdat.york.ac.uk"
    )
    parser.add_argument(
        "--token", help="Personal Access Token. Required for authentication"
    )

    args = parser.parse_args()

    pyro = read(args.filename)
    data = convert_to_omas(pyro)

    data["contributors"] = [
        {"name": contributor}
        for contributor in args.contributors or [args.filename.owner()]
    ]
    data["title"] = args.title or args.filename.name
    data["converged"] = not args.unconverged

    result_json = upload(args.filename, data, server=args.server, token=args.token)

    if not args.quiet:
        print(json.dumps(result_json))


if __name__ == "__main__":
    run()
