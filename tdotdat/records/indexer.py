# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 TDoTP.
#
# TDotDat is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Indexer for TDotDat."""


def indexer_receiver(sender, arguments=None, json=None, record=None,
                     index=None, doc_type=None):
    """Move _files key to files."""
    if '_files' in json:
        json['files'] = json['_files']
        del json['_files']
