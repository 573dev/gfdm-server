from v8_server.eamuse.xml.utils import load_xml_template


class Facility(object):
    """
    Handle the Facility request.

    The only method of note is the "get" method. This method expects to return a bunch
    of information about the arcade this cabinet is in, as well as some settings for
    URLs and the name of the cab.

    Example:
        <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
            <facility encoding="SHIFT_JIS" method="get"/>
        </call>
    """

    # Methods
    GET = "get"

    @classmethod
    def get(cls):
        # TODO: The facility data should be read in from a config file instead of being
        # hard coded here

        args = {
            "id": "CA-123",
            "country": "CA",
            "region": "MB",
            "name": "SenPi Arcade",
        }
        return load_xml_template("facility", "get", args)
