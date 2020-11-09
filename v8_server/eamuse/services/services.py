from __future__ import annotations

import logging
from binascii import unhexlify
from datetime import datetime
from enum import IntEnum
from random import randint
from time import time
from typing import Dict, Optional, Tuple, Union

from flask import Request
from kbinxml import KBinXML
from lxml import etree
from lxml.builder import E
from lxml.etree import _Element as eElement

from v8_server import LOG_PATH
from v8_server.eamuse.utils.arc4 import EAmuseARC4
from v8_server.eamuse.utils.eamuse import Model
from v8_server.eamuse.utils.lz77 import Lz77
from v8_server.eamuse.xml.utils import get_xml_attrib, get_xml_tag


# We want a general logger, and a special logger to log requests separately
logger = logging.getLogger(__name__)
rlogger = logging.getLogger("requests")


# Use an Enum for the different services for minimal xml
class ServiceType(IntEnum):
    PCBTRACKER = 1
    MESSAGE = 2
    PCBEVENT = 3
    FACILITY = 4
    PACKAGE = 5
    CARDMNG = 6
    LOCAL = 7
    DLSTATUS = 8


class Services(object):
    """
    Handles a service request from the eAmuse Server
    """

    # Default service url that GFDM uses. You will need to set up your network so that
    # this URL points to this server.
    # SERVICE_URL = "https://eamuse.konami.fun"
    SERVICE_URL = "https://e.k.f"

    # The base route that GFDM uses to query the eAmuse server to get the list of
    # offered services
    SERVICES_ROUTE = "/services/"

    # The custom route that we tell GFDM to use to query the eAmuse server
    SERVICE_ROUTE = "/service"

    # Default NTP url
    # XXX: Maybe needs to be configurable? What if the machine this is running on
    # doesn't have internet access?
    NTP_URL = "ntp://pool.ntp.org"

    def __init__(
        self,
        expire: int = 600,
        method: str = "get",
        mode: str = "operation",
        status: int = 0,
    ) -> None:
        self.expire = expire
        self.method = method
        self.mode = mode
        self.status = status
        self.services = self.generate_services()

    def get_services(self) -> etree:
        return E.response(
            E.services(
                expire=str(self.expire),
                method=self.method,
                mode=self.mode,
                status=str(self.status),
                *[E.item({"name": k, "url": self.services[k]}) for k in self.services],
            )
        )

    def generate_services(self) -> Dict[str, str]:
        # The Localhost IP Address
        ip = "127.0.0.1"
        services = {
            "ntp": self.NTP_URL,
            "keepalive": (
                f"{self.SERVICE_URL}/keepalive?"
                f"pa={ip}&ia={ip}&ga={ip}&ma={ip}&t1=2&t2=10"
            ),
            **{
                n.lower(): f"{self.SERVICE_URL}/{self.SERVICE_ROUTE}/{m}/"
                for n, m in ServiceType.__members__.items()
            },
        }
        return services

    def __repr__(self) -> str:
        return (
            f"Services<expire: {self.expire}, "
            f'method: "{self.method}", mode: "{self.mode}", status: {self.status}, '
            f"services: {list(self.services.keys())}>"
        )


class ServiceRequest(object):
    # eAmuse Header tags we care about
    X_EAMUSE_INFO = "x-eamuse-info"
    X_COMPRESS = "x-compress"

    # The encoding that we will use for this data
    ENCODING = "UTF-8"

    # Log dir for the requests
    LOG_DIR = LOG_PATH / "requests"

    # Static Request ID
    REQUEST_ID = 0

    def __init__(self, request: Request) -> None:
        # Save the request so we can refer back to it
        self._request = request

        self.model: Optional[Model] = None
        self.module: Optional[str] = None
        self.method: Optional[str] = None
        self.command: Optional[str] = None
        self.encrypted = self.X_EAMUSE_INFO in request.headers
        self.compression = (
            request.headers[self.X_COMPRESS]
            if self.X_COMPRESS in request.headers
            else "none"
        )
        self.compressed = self.compression != "none"

        # Parse the request data
        self.xml = self.read()

    def read(self) -> etree:
        # Lets grab the raw data from the request
        xml_bin = self._request.data

        # Decrypt the data if necessary
        x_eamuse_info: Optional[str] = None
        if self.encrypted:
            x_eamuse_info, key = self._get_encryption_data()
            xml_bin = EAmuseARC4(key).decrypt(xml_bin)

        # De-Compress the data if necessary
        # Right now we only support `lz77`
        if self.compressed and self.compression == "lz77":
            xml_bin = Lz77().decompress(xml_bin)

        # Convert the binary xml data to text bytes, and save a copy
        xml_bytes = KBinXML(xml_bin).to_text().encode(self.ENCODING)
        self._save_xml(xml_bytes, "req", x_eamuse_info)

        # Convert the XML text to an eTree
        xml_root = etree.fromstring(xml_bytes)

        # Grab the common xml information that we need
        # <call model="_MODEL_" srcid="_SRCID_">
        #     <_MODULE_ method="_METHOD_" command="_COMMAND_">
        # </call>

        # First grab the model
        self.model = Model.from_modelstring(get_xml_attrib(xml_root, "model"))

        # The module is the first child of the root
        module = xml_root[0]
        self.module = get_xml_tag(module)
        self.method = get_xml_attrib(module, "method")
        self.command = get_xml_attrib(module, "command")

        rlogger.info(self.__repr__())
        rlogger.debug(f"Request:\n {xml_bytes.decode(self.ENCODING)}")
        return xml_root

    def response(self, xml_bytes: Union[bytes, eElement]):
        # Firstly, let's make sure xml_bytes is a bytes object
        if type(xml_bytes) == eElement:
            xml_bytes = etree.tostring(xml_bytes, pretty_print=True)

        # Generate our own encryption key
        x_eamuse_info, key = self._make_encryption_data()

        # Save our xml response
        self._save_xml(xml_bytes, "resp", x_eamuse_info if self.encrypted else None)

        # Convert our xml to binary
        xml_bin = KBinXML(xml_bytes).to_binary()

        # Common Headers
        headers = {
            "Content-Type": "application/octet_stream",
            "Server": "Microsoft-HTTPAPI/2.0",
        }

        # Compress the data if necessary
        # Right now we only support `lz77`
        if self.compressed and self.compression == "lz77":
            xml_bin = Lz77().compress(xml_bin)
            headers[self.X_COMPRESS] = "lz77"

        # Encrypt the data if necessary
        if self.encrypted:
            xml_bin = EAmuseARC4(key).encrypt(xml_bin)
            headers[self.X_EAMUSE_INFO] = x_eamuse_info

        rlogger.debug(f"Response:\n{xml_bytes.decode(self.ENCODING)}")

        # Update the Static Request ID
        ServiceRequest.REQUEST_ID += 1

        return xml_bin, headers

    def _get_encryption_data(self) -> Tuple[str, bytes]:
        x_eamuse_info = self._request.headers[self.X_EAMUSE_INFO]
        key = unhexlify(x_eamuse_info[2:].replace("-", ""))
        return x_eamuse_info, key

    def _make_encryption_data(self) -> Tuple[str, bytes]:
        info = f"1-{int(time()):08x}-{randint(0x0000, 0xffff):04x}"
        key = unhexlify(info[2:].replace("-", ""))
        return info, key

    def _save_xml(self, data: bytes, kind: str, _id: Optional[str]) -> None:
        # Always make sure the dir exists
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)

        # We want a unique identifier to match requests and responses, so let's use the
        # x-eamuse-info header if it exists, else just a hash of the data
        uid = _id if _id is not None else str(abs(hash(self._request.data)))[0:8]

        # Write out the data
        date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        filepath = (
            self.LOG_DIR
            / f"eamuse_{date}_{uid}_{ServiceRequest.REQUEST_ID:04d}_{kind}.xml"
        )
        with filepath.open("wb") as f:
            logging.debug(f"Writing File: {filepath}")
            f.write(data)

    def __repr__(self) -> str:
        return (
            f'ServiceRequest<model: "{self.model}", module: "{self.module}", '
            f'method: "{self.method}", command: "{self.command}", '
            f"encrypted: {self.encrypted}, compressed: {self.compressed}, "
            f'compression: "{self.compression}">'
        )
