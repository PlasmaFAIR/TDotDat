# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 TDoTP.
#
# TDotDat is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Records API."""

import uuid

from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_pidstore import current_pidstore
from invenio_jsonschemas import current_jsonschemas
from invenio_records_files.api import Record as FilesRecord


class Record(FilesRecord):
    """Custom record."""

    _schema = "records/record-v1.0.0.json"

    @classmethod
    def create(cls, data, id_=None, **kwargs):
        data["$schema"] = current_jsonschemas.path_to_url(cls._schema)

        if "equilibrium_id" in data:
            data["equilibrium"] = {
                "$ref": f"http://tdotdat.com/resolver/equilibrium/{data['equilibrium_id']}"
            }

        return super().create(data, id_=id_, **kwargs)


def create_record(data):
    """Create a record.

    :param dict data: The record data.
    """
    with db.session.begin_nested():
        # create uuid
        rec_uuid = uuid.uuid4()
        # create PID
        current_pidstore.minters["recid"](rec_uuid, data)
        # create record
        created_record = Record.create(data, id_=rec_uuid)
        # index the record
        RecordIndexer().index(created_record)
    db.session.commit()
