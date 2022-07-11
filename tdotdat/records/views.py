# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 TDoTP.
#
# TDotDat is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Blueprint definitions."""

from operator import itemgetter
from os.path import splitext

from flask import Blueprint, request, abort
from invenio_previewer.proxies import current_previewer
from invenio_files_rest.models import ObjectVersion
from invenio_files_rest.views import ObjectResource
from invenio_records_ui.views import default_view_method


blueprint = Blueprint(
    "tdotdat_records",
    __name__,
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
