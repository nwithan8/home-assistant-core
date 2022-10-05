"""Constants for the EasyPost integration."""
from __future__ import annotations

from datetime import timedelta
from typing import Final
from logging import Logger, getLogger

import voluptuous as vol

import homeassistant.helpers.config_validation as cv

DEFAULT_NAME: Final = "EasyPost"
DOMAIN: Final = "easypost"
LOGGER: Logger = getLogger(__package__)

ICON: Final = "mdi:package-variant-closed"

MIN_TIME_BETWEEN_UPDATES: Final = timedelta(minutes=15)

CONF_CARRIER: Final = "carrier"
CONF_TRACKING_NUMBER: Final = "tracking_number"

SERVICE_ADD_TRACKER: Final = "add_tracker"

SERVICE_ADD_TRACKER_SCHEMA: Final = vol.Schema(
    {
        vol.Required(CONF_TRACKING_NUMBER): cv.string,
        vol.Required(CONF_CARRIER): cv.string,
    }
)

CARRIER_TRANSLATIONS: Final = {
    "AmazonMws": "AmazonMws",
    "APC": "APC",
    "Asendia": "Asendia",
    "Asendia USA": "AsendiaUsa",
    "Australia Post": "AustraliaPost",
    "AxlehireV3": "AxlehireV3",
    "Better Trucks": "BetterTrucks",
    "Bond": "Bond",
    "Canada Post": "CanadaPost",
    "Canpar": "Canpar",
    "CDL Last Mile Solutions": "ColumbusLastMile",
    "Chronopost": "Chronopost",
    "CloudSort": "CloudSort",
    "Courier Express": "CourierExpress",
    "CouriersPlease": "CouriersPlease",
    "Dai Post": "DaiPost",
    "Deutsche Post": "DeutschePost",
    "Deutsche Post UK": "DeutschePostUK",
    "DHL eCommerce Asia": "DHLEcommerceAsia",
    "DHL eCommerce Solutions": "DhlEcs",
    "DHL Express": "DHLExpress",
    "DPD": "DPD",
    "DPD UK": "DPDUK",
    "ePost Global": "ePostGlobal",
    "Estafeta": "Estafeta",
    "Evri": "Evri",
    "Fastway": "Fastway",
    "FedEx": "FedEx",
    "FedEx Cross Border": "FedExCrossBorder",
    "FedEx Mailview": "FedExMailview",
    "FedEx SameDay City": "FedExSameDayCity",
    "FedEx SmartPost": "FedexSmartPost",
    "FirstMile": "FirstMile",
    "Globegistics": "Globegistics",
    "GSO": "GSO",
    "Interlink Express": "InterlinkExpress",
    "JP Post": "JPPost",
    "Kuroneko Yamato": "KuronekoYamato",
    "La Poste": "LaPoste",
    "LaserShip": "LaserShipV2",
    "Loomis Express": "LoomisExpress",
    "LSO": "LSO",
    "Newgistics": "Newgistics",
    "OnTrac": "OnTrac",
    "Osm Worldwide": "OsmWorldwide",
    "Parcelforce": "Parcelforce",
    "PARCLL": "Parcll",
    "Passport": "PassportGlobal",
    "PostNL": "PostNL",
    "Purolator": "Purolator",
    "Royal Mail": "RoyalMail",
    "SEKO OmniParcel": "OmniParcel",
    "Sendle": "Sendle",
    "SF Express": "SFExpress",
    "Spee-Dee": "SpeeDee",
    "StarTrack": "StarTrack",
    "Swyft": "Swyft",
    "TForce Logistics": "TForce",
    "Toll": "Toll",
    "UDS": "UDS",
    "UPS": "UPS",
    "UPS i-parcel": "UPSIparcel",
    "UPS Mail Innovations": "UPSMailInnovations",
    "USPS": "USPS",
    "Veho": "Veho",
    "XDelivery": "XDelivery",
    "Yanwen": "Yanwen",
}
