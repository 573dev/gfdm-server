from v8_server.eamuse.xml.utils import load_xml_template


class DLStatus(object):
    """
    Handle the DLStatus request.

    It is unknown as to what this does.
    """

    # Methods
    PROGRESS = "progress"

    @classmethod
    def progress(cls):
        return load_xml_template("dlstatus", "progress")
