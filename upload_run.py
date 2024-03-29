#!/usr/bin/env python3

import argparse
import pathlib
import requests
import json
from urllib.parse import urljoin
from typing import List

import pyrokinetics


def read(filename: pathlib.Path) -> pyrokinetics.Pyro:
    pyro = pyrokinetics.Pyro(gk_file=filename)
    pyro.load_gk_output()

    return pyro


def upload(
    input_file: pathlib.Path,
    data: dict,
    outputs: List[pathlib.Path],
    server="https://localhost:5000",
    endpoint="api/records",
    token=None,
    quiet=False,
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
    new_id = r.json()["id"]
    result_json["files"] = []

    if not quiet:
        print(f"Created new record with ID: {new_id}")

    for filename in [input_file] + outputs:
        file_url = f"{url}/{new_id}/files/{filename.name}"

        with open(filename, "rb") as f:
            r = requests.put(file_url, data=f, verify=verify, headers=header)

        if not r.ok:
            raise RuntimeError(
                f"Server error on file upload ({r.status_code}): {r.json()}"
            )

        result_json["files"].append(r.json())

    return result_json


def run():
    parser = argparse.ArgumentParser("Upload simulation to TDoTDat")
    parser.add_argument("filename", help="Name of input file", type=pathlib.Path)
    parser.add_argument(
        "--outputs",
        help="Name of output file(s)",
        type=pathlib.Path,
        nargs="+",
        default=[],
    )
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

    data = read(args.filename).to_imas()
    data["contributors"] = [
        {"name": contributor}
        for contributor in args.contributors or [args.filename.owner()]
    ]
    data["title"] = args.title or args.filename.name
    data["converged"] = not args.unconverged

    result_json = upload(
        args.filename,
        data,
        args.outputs,
        server=args.server,
        token=args.token,
        quiet=args.quiet,
    )

    if not args.quiet:
        print(json.dumps(result_json))


if __name__ == "__main__":
    run()
