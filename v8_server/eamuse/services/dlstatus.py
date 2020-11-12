from lxml import etree

from v8_server.eamuse.services.services import ServiceRequest
from v8_server.eamuse.xml.utils import load_xml_template


class Progress(object):
    """
    Handle the DLStatus Progress request.

    It is unknown as to what this does.

    <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
        <dlstatus method="progress">
            <progress __type="s32">0</progress>
        </dlstatus>
    </call>
    """

    def __init__(self, req: ServiceRequest) -> None:
        self.progress_value = int(req.xml[0].find("progress").text)

    def progress(self) -> etree:
        return load_xml_template("dlstatus", "progress")

    def __repr__(self) -> str:
        return f"DLStatus.Progress<progress = {self.progress_value}>"
