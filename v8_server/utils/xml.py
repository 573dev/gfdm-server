import logging
from binascii import unhexlify
from datetime import datetime
from random import randint
from time import time
from typing import Dict, Optional, Tuple, Union

import lxml
from flask import Request
from kbinxml import KBinXML
from lxml import etree as ET  # noqa: N812

from v8_server import LOG_PATH
from v8_server.utils.arc4 import EamuseARC4
from v8_server.utils.lz77 import Lz77


# We want a general logger, and a special logger to log requests separately
logger = logging.getLogger(__name__)
rlogger = logging.getLogger("requests")

# eAmuse Header Tags
X_EAMUSE_INFO = "x-eamuse-info"
X_COMPRESS = "x-compress"


def is_encrypted(request: Request) -> bool:
    return X_EAMUSE_INFO in request.headers


def get_encryption_key(request: Request) -> Tuple[str, bytes]:
    info = request.headers[X_EAMUSE_INFO]
    key = unhexlify(info[2:].replace("-", ""))
    return info, key


def make_encryption_key() -> Tuple[str, bytes]:
    info = f"1-{int(time()):08x}-{randint(0x0000, 0xffff):04x}"
    key = unhexlify(info[2:].replace("-", ""))
    return info, key


def is_compressed(request: Request) -> bool:
    return X_COMPRESS in request.headers and request.headers[X_COMPRESS] != "none"


def get_compression_type(request: Request) -> str:
    return request.headers[X_COMPRESS]


def get_xml_tag(xml: lxml.etree._Element) -> str:
    return str(xml.tag)


def get_xml_attrib(xml: lxml.etree._Element, name: str) -> str:
    return str(xml.attrib[name]) if name in xml.attrib else "None"


def format_date(timestamp: Optional[int]) -> str:
    if timestamp is None:
        return "None"

    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def save_xml(data: bytes, request: Request, kind: str, _type: str = "xml") -> None:
    # Always make sure the dir exists
    dirpath = LOG_PATH / "requests"
    dirpath.mkdir(parents=True, exist_ok=True)

    # We want a unique identifier to match requests and responses, so lets use the
    # x-eamuse-info header if it exists, else just a hash of the data
    info = str(abs(hash(request.data)))[0:8]
    if is_encrypted(request):
        x_eamuse_info = get_encryption_key(request)[0]
        info = x_eamuse_info.replace("-", "_")[2:]

    # Write out the data
    date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    filepath = dirpath / f"eamuse_{date}_{info}_{kind}.{_type}"
    with filepath.open("wb") as f:
        logging.debug(f"Writing File: {filepath}")
        f.write(data)


def eamuse_read_xml(request: Request) -> Tuple[lxml.etree._Element, str, str, str, str]:
    # Get the raw xml data from the request
    xml_bin = request.data

    # Decrypt the data if necessary
    if is_encrypted(request):
        _, key = get_encryption_key(request)
        xml_bin = EamuseARC4(key).decrypt(xml_bin)

    # Decompress the data if necessary
    # Right now we only de-compress lz77
    if is_compressed(request) and get_compression_type(request) == "lz77":
        xml_bin = Lz77().decompress(xml_bin)

    # Convert the binary xml data to text bytes and save a copy
    try:
        xml_bytes = KBinXML(xml_bin).to_text().encode("UTF-8")
    except Exception:
        print(xml_bin)
        raise
    save_xml(xml_bytes, request, "req")

    # Convert the xml text to an eTree
    root = ET.fromstring(xml_bytes)

    # Grab the xml information we care about
    model = get_xml_attrib(root, "mode")
    module = get_xml_tag(root[0])
    method = get_xml_attrib(root[0], "method")
    command = get_xml_attrib(root[0], "command")

    rlogger.debug(
        "---- Request ----\n"
        f"[ {'Model':^20} | {'Module':^15} | {'Method':^15} | {'Command':^20} ]\n"
        f"[ {model:^20} | {module:^15} | {method:^15} | {command:^20} ]\n"
        f"{xml_bytes.decode('UTF-8')}\n"
    )

    # Return XML and important fields
    return root, model, module, method, command


def eamuse_prepare_xml(
    xml_bytes: Union[bytes, lxml.etree._Element], request: Request
) -> Tuple[bytes, Dict[str, str]]:
    # Make sure xml_bytes is a bytes object
    if type(xml_bytes) == lxml.etree._Element:
        xml_bytes = ET.tostring(xml_bytes, pretty_print=True)

    # Lets save our response
    save_xml(xml_bytes, request, "resp")

    # Lets make our own encryption key
    x_eamuse_info, key = make_encryption_key()

    # Common headers
    headers = {
        "Content-Type": "applicaton/octet_stream",
        "Server": "Microsoft-HTTPAPI/2.0",
    }

    # Convert XML to binary and save
    xml_bin = KBinXML(xml_bytes).to_binary()

    # TODO: I don't know that we really need to save the binary xml
    # save_xml(xml_bin, request, "resp", _type="bin")

    # Compress if necessary
    # Right now we only compress lz77
    if is_compressed(request) and get_compression_type(request) == "lz77":
        headers[X_COMPRESS] = "lz77"
        xml_bin = Lz77().compress(xml_bin)

    # Encrypt if necessary
    if is_encrypted(request):
        headers[X_EAMUSE_INFO] = x_eamuse_info
        xml_bin = EamuseARC4(key).encrypt(xml_bin)

    rlogger.debug(f"---- Response ----\n{xml_bytes.decode('UTF-8')}\n")

    return xml_bin, headers
