# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 TDoTP.
#
# TDotDat is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""JS/CSS Webpack bundle to override search results template."""

from invenio_assets.webpack import WebpackThemeBundle

search_app = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "bootstrap3": dict(entry={}, dependencies={}, aliases={}),
        "semantic-ui": dict(
            entry={
                "tdotdat-search-app": "./js/tdotdat_records/index.js",
                "tdotdat-deposit-app": "./js/tdotdat_records/deposit/index.js",
            },
            dependencies={
                "react": "^16.9.0",
                "react-dom": "^16.9.0",
                "react-overridable": "^0.0.2",
                "semantic-ui-react": "^0.88.0",
            },
        ),
    },
)
