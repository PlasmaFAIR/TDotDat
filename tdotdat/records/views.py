# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 TDoTP.
#
# TDotDat is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Blueprint definitions."""

from operator import itemgetter
from os.path import splitext
import json
from io import BytesIO
import copy
import pathlib
import tempfile

from flask import (
    Blueprint,
    request,
    abort,
    redirect,
    url_for,
    render_template,
    current_app,
    send_file,
)
from flask_login import login_required
from invenio_previewer.proxies import current_previewer
from invenio_files_rest.models import ObjectVersion, Bucket
from invenio_files_rest.views import ObjectResource
from invenio_records_ui.views import default_view_method
from invenio_records_ui.signals import record_viewed
from invenio_pidstore.resolver import Resolver
from invenio_pidstore.errors import (
    PIDDoesNotExistError,
    PIDMissingObjectError,
    PIDRedirectedError,
    PIDUnregistered,
)
from invenio_jsonschemas import current_jsonschemas
from werkzeug.routing import BuildError, BaseConverter

import pyrokinetics

from .forms import RecordForm
from .api import create_record, Record
from .serializers import json_v1


blueprint = Blueprint(
    "tdotdat_records",
    __name__,
    url_prefix="/records",
    template_folder="templates",
    static_folder="static",
)
"""Blueprint used for loading templates and static assets

The sole purpose of this blueprint is to ensure that Invenio can find the
templates and static files located in the folders of the same names next to
this file.
"""


class IntListConverter(BaseConverter):
    """Match ints separated with ','.

    Adapted from https://stackoverflow.com/a/32237936/2043465
    """

    # at least one int, separated by ,, with optional trailing ,
    regex = r"\d+(?:,\d+)*,?"

    # this is used to parse the url and pass the list to the view function
    def to_python(self, value):
        return [int(x) for x in value.split(",")]

    # this is used when building a url with url_for
    def to_url(self, value):
        return ",".join(str(x) for x in value)


#
# Files related template filters.
#
@blueprint.app_template_filter()
def select_preview_file(files):
    """Get list of files and select one for preview."""
    selected = None

    try:
        for f in sorted(files or [], key=itemgetter("key")):
            file_type = splitext(f["key"])[1][1:].lower()
            if file_type in current_previewer.previewable_extensions:
                if selected is None:
                    selected = f
                elif f["default"]:
                    selected = f
    except KeyError:
        pass
    return selected


def record_file_factory(pid, record, filename):
    """Get file from a record.
    :param pid: Not used. It keeps the function signature.
    :param record: Record which contains the files.
    :param filename: Name of the file to be returned.
    :returns: File object or ``None`` if not found.
    """

    try:
        files = {f["key"]: f for f in record["_files"]}
        return ObjectVersion.get(files[filename]["bucket"], filename)
    except KeyError:
        return None


def file_download_ui(pid, record, _record_file_factory=None, **kwargs):
    """File download view for a given record.

    Patched version from invenio-records-ui

    If ``download`` is passed as a querystring argument, the file is sent as an
    attachment.
    :param pid: The :class:`invenio_pidstore.models.PersistentIdentifier`
        instance.
    :param record: The record metadata.
    """
    _record_file_factory = _record_file_factory or record_file_factory
    # Extract file from record.
    fileobj = _record_file_factory(pid, record, kwargs.get("filename"))

    if not fileobj:
        abort(404)

    # Check permissions
    ObjectResource.check_object_permission(fileobj)

    # Send file.
    return fileobj.send_file(
        kwargs.get("filename"), as_attachment=bool(request.args.get("download"))
    )


def record_view(pid, record, template=None, **kwargs):
    r"""Display default view, but with references replaced

    Sends record_viewed signal and renders template.

    :param pid: PID object.
    :param record: Record object.
    :param template: Template to render.
    :param \*\*kwargs: Additional view arguments based on URL rule.
    :returns: The rendered template.
    """

    return default_view_method(pid, record.replace_refs(), template, **kwargs)


@blueprint.route("/create", methods=("GET", "POST"))
@login_required
def create():
    form = RecordForm()
    if not form.validate_on_submit():
        return render_template("records/create.html", form=form)

    contributors = [dict(name=form.contributor_name.data)]
    bucket = Bucket.create()
    data = {}
    pyro = None

    # We have a small problem: Pyrokinetics (currently) might rely on the actual
    # filenames of GK input/output files (for at least some GK codes). But the
    # uploaded files will be stored on disk with names like "<hash>/data". So,
    # we create a temporary directory, and we create symlinks there with the
    # actual filenames of the uploaded files (just the filename part, not the
    # full path). The tempdir gets cleaned up automatically
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = pathlib.Path(tmpdir)

        def store_file(file_):
            """Store file in bucket, make temporary symlink for Pyrokinetics"""
            file_storage = ObjectVersion.create(bucket, file_.filename, stream=file_)

            file_symlink = tmpdir_path / pathlib.Path(file_.filename).name
            file_symlink.symlink_to(file_storage.file.storage().fileurl)
            return file_storage.key, file_symlink

        if form.input_file.data:
            input_file = request.files[form.input_file.name]
            input_key, input_symlink = store_file(input_file)

            # Note this relies on details of the file storage to get the filename
            pyro = pyrokinetics.Pyro(gk_file=input_symlink)
            data.update({"input_files": [input_key], **pyro.to_imas()})
        else:
            data.update({"software": {"name": form.software.data}})

        if form.output_file.data:
            if pyro is None:
                raise RuntimeError("Missing input file")

            keys = []
            for output_file in request.files.getlist(form.output_file.name):
                key, _ = store_file(output_file)
                keys.append(key)

            pyro.load_gk_output()
            data.update({"output_files": keys, **pyro.to_imas()})

    files = [
        dict(
            key=f.key,
            file_id=str(f.file_id),
            bucket=str(bucket.id),
            size=f.file.size,
            checksum=f.file.checksum,
            version_id=str(f.version_id),
        )
        for f in ObjectVersion.get_by_bucket(bucket.id)
    ]

    create_record(
        dict(
            title=form.title.data,
            contributors=contributors,
            _bucket=str(bucket.id),
            _files=files,
            **data,
        )
    )
    return redirect(url_for("tdotdat_records.success"))


@blueprint.route("/success")
@login_required
def success():
    return render_template("records/success.html")


@blueprint.route("/compare/<int_list:pid_value_list>")
def compare(pid_value_list):
    """Display multiple records at once. Takes a comma-separated list of PIDs"""

    resolver = Resolver(pid_type="recid", object_type="rec", getter=Record.get_record)

    try:
        record_list = [resolver.resolve(pid_value) for pid_value in pid_value_list]
    except (PIDDoesNotExistError, PIDUnregistered):
        abort(404)
    except PIDMissingObjectError as e:
        current_app.logger.exception(
            "No object assigned to {0}.".format(e.pid), extra={"pid": e.pid}
        )
        abort(500)
    except PIDRedirectedError as e:
        try:
            return redirect(
                url_for(
                    ".{0}".format(e.destination_pid.pid_type),
                    pid_value=e.destination_pid.pid_value,
                )
            )
        except BuildError:
            current_app.logger.exception(
                "Invalid redirect - pid_type '{0}' endpoint missing.".format(
                    e.destination_pid.pid_type
                ),
                extra={
                    "pid": e.pid,
                    "destination_pid": e.destination_pid,
                },
            )
            abort(500)

    for pid, record in record_list:
        record_viewed.send(current_app._get_current_object(), pid=pid, record=record)

    return render_template(
        "records/compare.html", record_list=record_list, pid_value_list=pid_value_list
    )


@blueprint.route("/download/<int_list:pid_value_list>")
def download(pid_value_list):
    """Download multiple records. Takes a comma-separated list of PIDs"""

    resolver = Resolver(pid_type="recid", object_type="rec", getter=Record.get_record)

    try:
        record_list = [resolver.resolve(pid_value) for pid_value in pid_value_list]
    except (PIDDoesNotExistError, PIDUnregistered):
        abort(404)
    except PIDMissingObjectError as e:
        current_app.logger.exception(
            "No object assigned to {0}.".format(e.pid), extra={"pid": e.pid}
        )
        abort(500)
    except PIDRedirectedError as e:
        try:
            return redirect(
                url_for(
                    ".{0}".format(e.destination_pid.pid_type),
                    pid_value=e.destination_pid.pid_value,
                )
            )
        except BuildError:
            current_app.logger.exception(
                "Invalid redirect - pid_type '{0}' endpoint missing.".format(
                    e.destination_pid.pid_type
                ),
                extra={
                    "pid": e.pid,
                    "destination_pid": e.destination_pid,
                },
            )
            abort(500)

    for pid, record in record_list:
        record_viewed.send(current_app._get_current_object(), pid=pid, record=record)

    serialised = json.dumps(
        [
            json_v1.transform_record(pid, record)["metadata"]
            for (pid, record) in record_list
        ]
    )

    return send_file(
        BytesIO(serialised.encode("utf-8")),
        mimetype="application/json",
        download_name="results.json",
        as_attachment=True,
    )

    return render_template("records/compare.html", record_list=record_list)


@blueprint.route("/plot")
def plot():
    return render_template("records/plot.html")


@blueprint.route("/reference")
def reference():
    schema = copy.deepcopy(current_jsonschemas.get_schema(Record._schema))["properties"]
    DROP_KEYS = ["$schema", "_bucket", "_files"]
    for key in DROP_KEYS:
        del schema[key]

    def flatten_dict(data, parent=None):
        result = {}
        for key, value in data.items():
            name = f"{parent}.{key}" if parent else key
            result[name] = {
                "type": value["type"],
                "description": value.get("description", ""),
            }
            result.update(flatten_dict(value.get("properties", {}), parent=name))
            result.update(
                flatten_dict(value.get("items", {}).get("properties", {}), parent=name)
            )
        return result

    return render_template("records/reference.html", schema=flatten_dict(schema))
