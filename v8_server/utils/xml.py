from binascii import unhexlify
from pathlib import Path
from random import randint
from time import time
from typing import Dict, Tuple

import lxml
import lzss
from flask import Request
from kbinxml import KBinXML
from lxml import etree as ET  # noqa: N812

from v8_server.utils.arc4 import EamuseARC4
from v8_server.utils.eamuse import get_timestamp


EAMUSE_CONFIG = {"encrypted": False, "compressed": False}
REQUESTS_PATH = Path("./requests")


def eamuse_read_xml(request: Request) -> Tuple[str, str, str, str, str]:
    # Get encrypted/compressed data from client
    headers = request.headers
    data = request.data

    if "x-eamuse-info" in headers:
        # Decrypt/Compress data
        x_eamuse_info = headers["x-eamuse-info"]
        key = unhexlify(x_eamuse_info[2:].replace("-", ""))
        arc4 = EamuseARC4(key)
        xml_dec = arc4.decrypt(data)
        EAMUSE_CONFIG["encrypted"] = True
    else:
        xml_dec = data
        EAMUSE_CONFIG["encrypted"] = False

    compress = headers["x-compress"] if "x-compress" in headers else None

    if compress == "lz77":
        xml_dec = lzss.decompress(xml_dec)
        EAMUSE_CONFIG["compress"] = True
    else:
        EAMUSE_CONFIG["compress"] = False

    xml_text = KBinXML(xml_dec).to_text().encode("UTF-8")

    root = ET.fromstring(xml_text)

    REQUESTS_PATH.mkdir(exist_ok=True)
    output_filename = REQUESTS_PATH / f"eamuse_{get_timestamp()}_req.xml"
    with output_filename.open("w") as f:
        f.write(xml_text.decode("UTF-8"))

    model = root.attrib["model"]
    module = root[0].tag
    method = root[0].attrib["method"] if "method" in root[0].attrib else None
    command = root[0].attrib["command"] if "command" in root[0].attrib else None

    print(
        "---- Read Request ----\n"
        f"Headers: [{dict(headers)}]\n"
        f"  Model: [{model}]\n"
        f" Module: [{module}]\n"
        f" Method: [{method}]\n"
        f"Command: [{command}]\n"
        "   Data:\n"
        f"{xml_text.decode('UTF-8')[:-1]}\n"
    )

    # Return raw XML
    return xml_text, model, module, method, command


def eamuse_prepare_xml(xml: str) -> Tuple[bytes, Dict[str, str]]:
    x_eamuse_info = f"1-{int(time()):08x}-{randint(0x0000, 0xffff):04x}"
    key = unhexlify(x_eamuse_info[2:].replace("-", ""))

    xml_root = xml
    if type(xml) == lxml.etree._Element:
        xml = ET.tostring(xml, encoding="UTF-8").decode("UTF-8")

    REQUESTS_PATH.mkdir(exist_ok=True)
    timestamp = get_timestamp()
    output_filename = REQUESTS_PATH / f"eamuse_{timestamp}_resp.xml"
    with output_filename.open("wb") as f:
        f.write(xml.encode("UTF-8"))

    headers = {
        "Content-Type": "applicaton/octet_stream",
        "Server": "Microsoft-HTTPAPI/2.0",
    }

    # Convert XML to binary
    xml_bin = KBinXML(xml.encode("UTF-8")).to_binary()
    output_filename = REQUESTS_PATH / f"eamuse_{timestamp}_resp.bin"
    with output_filename.open("wb") as f:
        f.write(xml_bin)

    if EAMUSE_CONFIG["compress"]:
        headers["X-Compress"] = "lz77"
        # Actually do some compression here if we have to

    headers["X-Eamuse-Info"] = x_eamuse_info

    if EAMUSE_CONFIG["encrypted"]:
        arc4 = EamuseARC4(key)
        data = arc4.encrypt(xml_bin)
    else:
        data = xml_bin

    print(
        "---- Write Response ----\n"
        "   Data: [\n"
        f"{ET.tostring(xml_root, pretty_print=True).decode('UTF-8')[:-1]}\n"
        f"Headers: [{headers}]\n"
    )

    return data, headers
