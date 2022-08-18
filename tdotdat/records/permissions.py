# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 TDoTP.
#
# TDotDat is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Permissions for TDotDat."""

from invenio_access import Permission, authenticated_user


def files_permission_factory(obj, action=None):
    """Permissions factory for buckets."""
    return Permission(authenticated_user)


def authenticated_user_permission(record=None):
    """Permissions factory for checking for authenticated users"""
    return Permission(authenticated_user)
