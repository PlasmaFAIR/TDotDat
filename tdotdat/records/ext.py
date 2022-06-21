# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 TDoTP.
#
# TDotDat is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Flask extension for TDotDat."""

from invenio_files_rest.signals import file_deleted, file_uploaded
from invenio_indexer.signals import before_record_index

from . import config, indexer
from .tasks import update_record_files_async


class TDotDat(object):
    """TDotDat extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions['tdotdat'] = self
        self._register_signals(app)

    def init_config(self, app):
        """Initialize configuration.

        Override configuration variables with the values in this package.
        """
        with_endpoints = app.config.get(
            'TDOTDAT_ENDPOINTS_ENABLED', True)
        for k in dir(config):
            if k.startswith('TDOTDAT_'):
                app.config.setdefault(k, getattr(config, k))
            elif k == 'SEARCH_UI_SEARCH_TEMPLATE':
                app.config['SEARCH_UI_SEARCH_TEMPLATE'] = getattr(
                    config, k)
            elif k == 'PIDSTORE_RECID_FIELD':
                app.config['PIDSTORE_RECID_FIELD'] = getattr(config, k)
            elif k == 'FILES_REST_PERMISSION_FACTORY':
                app.config['FILES_REST_PERMISSION_FACTORY'] =\
                        getattr(config, k)
            else:
                for n in ['RECORDS_REST_ENDPOINTS', 'RECORDS_UI_ENDPOINTS',
                          'RECORDS_REST_FACETS', 'RECORDS_REST_SORT_OPTIONS',
                          'RECORDS_REST_DEFAULT_SORT',
                          'RECORDS_FILES_REST_ENDPOINTS']:
                    if k == n and with_endpoints:
                        app.config.setdefault(n, {})
                        app.config[n].update(getattr(config, k))

    def _register_signals(self, app):
        """Register signals."""
        before_record_index.dynamic_connect(
            indexer.indexer_receiver,
            sender=app,
            index="records-record-v1.0.0")

        file_deleted.connect(update_record_files_async, weak=False)
        file_uploaded.connect(update_record_files_async, weak=False)
