from invenio_assets.webpack import WebpackThemeBundle

search_app = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "bootstrap3": dict(entry={}, dependencies={}, aliases={}),
        "semantic-ui": dict(
            entry={
                "tdotdat-equilibrium-search-app": "./js/tdotdat_equilibrium/index.js",
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
