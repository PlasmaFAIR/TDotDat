from invenio_indexer.signals import before_record_index
from invenio_files_rest.signals import file_deleted, file_uploaded

from . import config, indexer
from .tasks import update_record_files_async


class Equilibrium:
    """Plasma equilibrium model"""

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.init_config(app)
        app.extensions["equilibrium"] = self
        self._register_signals(app)

    def init_config(self, app):
        with_endpoints = app.config.get("EQUILIBRIUM_ENDPOINTS_ENABLED", True)

        for k in dir(config):
            if k.startswith("EQUILIBRIUM_"):
                app.config.setdefault(k, getattr(config, k))
            elif k in [
                "SEARCH_UI_SEARCH_TEMPLATE",
                "PIDSTORE_RECID_FIELD",
                "FILES_REST_PERMISSION_FACTORY",
            ]:
                app.config[k] = getattr(config, k)
            elif with_endpoints and k in [
                "RECORDS_REST_ENDPOINTS",
                "RECORDS_UI_ENDPOINTS",
                "RECORDS_REST_FACETS",
                "RECORDS_REST_SORT_OPTIONS",
                "RECORDS_REST_DEFAULT_SORT",
                "RECORDS_FILES_REST_ENDPOINTS",
            ]:
                app.config.setdefault(k, {})
                app.config[k].update(getattr(config, k))

    def _register_signals(self, app):
        before_record_index.dynamic_connect(
            indexer.indexer_receiver, sender=app, index="equilibrium-equilibrium-v1.0.0"
        )

        file_deleted.connect(update_record_files_async, weak=False)
        file_uploaded.connect(update_record_files_async, weak=False)
