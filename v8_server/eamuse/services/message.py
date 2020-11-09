from v8_server.eamuse.xml.utils import load_xml_template


class Message(object):
    """
    Handle the Message request.

    It is unknown as to what this does. Possibly it's for operator messages

    Example:
        <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
            <message method="get"/>
        </call>
    """

    # Methods
    GET = "get"

    @classmethod
    def get(cls):
        return load_xml_template("message", "get")
