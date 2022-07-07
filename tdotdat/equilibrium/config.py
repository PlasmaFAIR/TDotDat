from invenio_indexer.api import RecordIndexer
from invenio_records_rest.utils import allow_all, check_elasticsearch
from invenio_search import RecordsSearch

from tdotdat.equilibrium.api import Equilibrium


def _(x):
    """Identity function for string extraction."""
    return x


RECORDS_REST_ENDPOINTS = {
    "equid": dict(
        pid_type="equid",
        pid_minter="equid",
        pid_fetcher="equid",
        default_endpoint_prefix=True,
        record_class=Equilibrium,
        search_class=RecordsSearch,
        indexer_class=RecordIndexer,
        search_index="equilibrium",
        search_type=None,
        record_serializers={
            "application/json": "tdotdat.equilibrium.serializers:json_v1_response",
        },
        search_serializers={
            "application/json": "tdotdat.equilibrium.serializers:json_v1_search",
        },
        record_loaders={
            "application/json": "tdotdat.equilibrium.loaders:json_v1",
        },
        list_route="/equilibrium/",
        item_route="/equilibrium/<pid(equid, record_class='tdotdat.equilibrium.api.Equilibrium'):pid_value>",
        default_media_type="application/json",
        max_result_window=10000,
        error_handlers=dict(),
        create_permission_factory_imp=allow_all,
        read_permission_factory_imp=check_elasticsearch,
        update_permission_factory_imp=allow_all,
        delete_permission_factory_imp=allow_all,
        list_permission_factory_imp=allow_all,
        # links_factory_imp="invenio_equilibrium_files."
        # "links:default_record_files_links_factory",
    ),
}
"""REST API for equilibrium."""


RECORDS_REST_SORT_OPTIONS = dict(
    equilibrium=dict(
        bestmatch=dict(
            title=_("Best match"),
            fields=["_score"],
            default_order="desc",
            order=1,
        ),
        mostrecent=dict(
            title=_("Most recent"),
            fields=["-_created"],
            default_order="asc",
            order=2,
        ),
    )
)
"""Setup sorting options."""


RECORDS_REST_DEFAULT_SORT = dict(
    equilibrium=dict(
        query="bestmatch",
        noquery="mostrecent",
    )
)
"""Set default sorting options."""

RECORDS_UI_ENDPOINTS = dict(
    equid=dict(
        pid_type="equid",
        route="/equilibrium/<pid_value>",
        template="equilibrium/record.html",
        record_class="tdotdat.equilibrium.api:Equilibrium",
    ),
    equid_previewer=dict(
        pid_type="equid",
        route="/equilibrium/<pid_value>/preview/<path:filename>",
        view_imp="invenio_previewer.views:preview",
        record_class="tdotdat.equilibrium.api:Equilibrium",
    ),
    equid_files=dict(
        pid_type="equid",
        route="/equilibrium/<pid_value>/files/<path:filename>",
        view_imp="tdotdat.records.views:file_download_ui",
        record_class="tdotdat.equilibrium.api:Equilibrium",
    ),
)
"""Records UI for tdotdat."""
