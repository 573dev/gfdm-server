from lxml.builder import E

from v8_server.eamuse.utils.xml import XMLBinTypes as T, e_type


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
        """
        Example:
            <response>
                <facility expire="600">
                    <location>
                        <id>US-123</id>
                        <country>US</country>
                        <region>.</region>
                        <name>H</name>
                        <type __type="u8">0</type>
                    </location>
                    <line>
                        <id>.</id>
                        <class __type="u8">0</class>
                    </line>
                    <portfw>
                        <globalip __type="ip4" __count="1">127.0.0.1</globalip>
                        <globalport __type="u16">80</globalport>
                        <privateport __type="u16">80</privateport>
                    </portfw>
                    <public>
                        <flag __type="u8">1</flag>
                        <name>.</name>
                        <latitude>0</latitude>
                        <longitude>0</longitude>
                    </public>
                    <share>
                        <eacoin>
                            <notchamount __type="s32">3000</notchamount>
                            <notchcount __type="s32">3</notchcount>
                            <supplylimit __type="s32">10000</supplylimit>
                        </eacoin>
                        <eapass>
                            <valid __type="u16">365</valid>
                        </eapass>
                        <url>
                            <eapass>www.ea-pass.konami.net</eapass>
                            <arcadefan>www.konami.jp/am</arcadefan>
                            <konaminetdx>http://am.573.jp</konaminetdx>
                            <konamiid>http://id.konami.net</konamiid>
                            <eagate>http://eagate.573.jp</eagate>
                        </url>
                    </share>
                </facility>
            </response>
        """

        # TODO: The facility data should be read in from a config file instead of being
        # hard coded here

        return E.response(
            E.facility(
                E.location(
                    E.id("CA-123"),
                    E.country("CA"),
                    E.region("MB"),
                    E.name("SenPi Arcade"),
                    E.type("0", e_type(T.u8)),
                ),
                E.line(E.id("."), E("class", "0", e_type(T.u8))),
                E.portfw(
                    E.globalip("127.0.0.1", e_type(T.ip4, count=1)),
                    E.globalport("80", e_type(T.u16)),
                    E.privateport("80", e_type(T.u16)),
                ),
                E.public(
                    E.flag("1", e_type(T.u8)),
                    E.name("Gotem"),
                    E.latitude("0"),
                    E.longitude("0"),
                ),
                E.share(
                    E.eacoin(
                        E.notchamount("3000", e_type(T.s32)),
                        E.notchcount("3", e_type(T.s32)),
                        E.supplylimit("10000", e_type(T.s32)),
                    ),
                    E.eapass(E.valid("365", e_type(T.u16))),
                    E.url(
                        E.eapass("www.ea-pass.konami.net"),
                        E.arcadefan("www.konami.jp/am"),
                        E.konaminetdx("http://am.573.jp"),
                        E.konamiid("http://id.konami.net"),
                        E.eagate("http://eagate.573.jp"),
                    ),
                ),
                {"expire": "600"},
            )
        )
