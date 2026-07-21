"""Exceptions for the Malta Met Office integration."""

from __future__ import annotations


class MaltaMetOfficeError(Exception):
    """Base Malta Met Office error."""


class MaltaMetOfficeConnectionError(MaltaMetOfficeError):
    """Connection error."""


class MaltaMetOfficeParseError(MaltaMetOfficeError):
    """Parse error."""


class MaltaMetOfficeEndpointError(MaltaMetOfficeError):
    """Endpoint returned unusable data."""
