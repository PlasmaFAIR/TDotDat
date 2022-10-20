# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 TDoTP.
#
# TDotDat is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Default configuration."""

from invenio_indexer.api import RecordIndexer
from invenio_records_rest.facets import terms_filter
from invenio_records_rest.utils import allow_all, check_search, deny_all
from invenio_search import RecordsSearch

from tdotdat.records.api import Record
from tdotdat.records.permissions import authenticated_user_permission


def _(x):
    """Identity function for string extraction."""
    return x


RECORDS_REST_ENDPOINTS = {
    'recid': dict(
        pid_type='recid',
        pid_minter='recid',
        pid_fetcher='recid',
        default_endpoint_prefix=True,
        record_class=Record,
        search_class=RecordsSearch,
        indexer_class=RecordIndexer,
        search_index='records',
        record_serializers={
            'application/json': ('tdotdat.records.serializers'
                                 ':json_v1_response'),
        },
        search_serializers={
            'application/json': ('tdotdat.records.serializers'
                                 ':json_v1_search'),
        },
        record_loaders={
            'application/json': ('tdotdat.records.loaders'
                                 ':json_v1'),
        },
        list_route='/records/',
        item_route='/records/<pid(recid,'
                   'record_class="tdotdat.records.api.Record")'
                   ':pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        error_handlers=dict(),
        create_permission_factory_imp=authenticated_user_permission,
        read_permission_factory_imp=check_search,
        update_permission_factory_imp=authenticated_user_permission,
        delete_permission_factory_imp=deny_all,
        list_permission_factory_imp=allow_all,
        links_factory_imp='invenio_records_files.'
                          'links:default_record_files_links_factory',
    ),
}
"""REST API for tdotdat."""

RECORDS_UI_ENDPOINTS = dict(
    recid=dict(
        pid_type='recid',
        route='/records/<pid_value>',
        template='records/record.html',
        record_class='tdotdat.records.api:Record',
        view_imp="tdotdat.records.views:record_view",
    ),
    recid_previewer=dict(
        pid_type='recid',
        route='/records/<pid_value>/preview/<path:filename>',
        view_imp='invenio_previewer.views:preview',
        record_class='tdotdat.records.api:Record',
    ),
    recid_files=dict(
        pid_type='recid',
        route='/records/<pid_value>/files/<path:filename>',
        view_imp='tdotdat.records.views:file_download_ui',
        record_class='tdotdat.records.api:Record',
    ),
)
"""Records UI for tdotdat."""

SEARCH_UI_SEARCH_TEMPLATE = 'records/search.html'

PIDSTORE_RECID_FIELD = 'id'

TDOTDAT_ENDPOINTS_ENABLED = True
"""Enable/disable automatic endpoint registration."""


RECORDS_REST_FACETS = dict(
    records=dict(
        aggs=dict(
            nonlinear=dict(terms=dict(field='model.non_linear_run')),
            software={"terms": {"field": "software.name"}},
            keywords=dict(terms=dict(field='keywords')),
            converged={"terms": {"field": "converged"}},
        ),
        post_filters=dict(
            nonlinear=terms_filter('model.non_linear_run'),
            software=terms_filter("software.name"),
            keywords=terms_filter('keywords'),
            converged=terms_filter("converged"),
        )
    )
)
"""Introduce searching facets."""


RECORDS_REST_SORT_OPTIONS = dict(
    records=dict(
        bestmatch=dict(
            title=_('Best match'),
            fields=['_score'],
            default_order='desc',
            order=1,
        ),
        mostrecent=dict(
            title=_('Most recent'),
            fields=['-_created'],
            default_order='asc',
            order=2,
        ),
    )
)
"""Setup sorting options."""


RECORDS_REST_DEFAULT_SORT = dict(
    records=dict(
        query='bestmatch',
        noquery='mostrecent',
    )
)
"""Set default sorting options."""

RECORDS_FILES_REST_ENDPOINTS = {
    'RECORDS_REST_ENDPOINTS': {
        'recid': '/files'
    },
}
"""Records files integration."""

FILES_REST_PERMISSION_FACTORY = \
    'tdotdat.records.permissions:files_permission_factory'
"""Files-REST permissions factory."""
