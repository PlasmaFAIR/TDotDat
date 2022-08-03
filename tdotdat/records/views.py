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
from werkzeug.routing import BuildError

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
    if form.validate_on_submit():
        contributors = [dict(name=form.contributor_name.data)]

        bucket = Bucket.create()

        inputs = {}
        if form.input_file.data:
            input_file = request.files[form.input_file.name]
            in_file = ObjectVersion.create(
                bucket, input_file.filename, stream=input_file
            )

            # Note this relies on details of the file storage to get the filename
            pyro = pyrokinetics.Pyro(gk_file=in_file.file.storage().fileurl)

            inputs["temperature"] = pyro.local_species["electron"].temp
            inputs["temperature_gradient"] = pyro.local_species["electron"].a_lt
            inputs["files"] = [in_file.key]

            software_name = pyro.gk_code
        else:
            in_file = None
            software_name = form.software.data

        outputs = {}
        if form.output_file.data:
            output_file = request.files[form.output_file.name]
            out_file = ObjectVersion.create(
                bucket, output_file.filename, stream=output_file
            )
            outputs["files"] = [out_file.key]

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
                software={"name": software_name},
                contributors=contributors,
                inputs=inputs,
                outputs=outputs,
                _bucket=str(bucket.id),
                _files=files,
                equilibrium_id=form.equilibrium_id.data,
            )
        )
        return redirect(url_for("tdotdat_records.success"))
    return render_template("records/create.html", form=form)


@blueprint.route("/success")
@login_required
def success():
    return render_template("records/success.html")


@blueprint.route("/compare/<pid_value_list>")
def compare(pid_value_list):
    """Display multiple records at once. Takes a comma-separated list of PIDs"""

    resolver = Resolver(pid_type="recid", object_type="rec", getter=Record.get_record)

    try:
        record_list = [
            resolver.resolve(pid_value) for pid_value in pid_value_list.split(",")
        ]
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


@blueprint.route("/download/<pid_value_list>")
def download(pid_value_list):
    """Download multiple records. Takes a comma-separated list of PIDs"""

    resolver = Resolver(pid_type="recid", object_type="rec", getter=Record.get_record)

    try:
        record_list = [
            resolver.resolve(pid_value) for pid_value in pid_value_list.split(",")
        ]
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
