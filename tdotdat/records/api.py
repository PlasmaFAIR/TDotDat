# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 TDoTP.
#
# TDotDat is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Records API."""

from invenio_records_files.api import Record as FilesRecord


class Record(FilesRecord):
    """Custom record."""

    _schema = "records/record-v1.0.0.json"
