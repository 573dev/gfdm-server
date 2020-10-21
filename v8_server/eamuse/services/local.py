from lxml import etree
from lxml.builder import E

from v8_server.eamuse.services.services import ServiceRequest
from v8_server.eamuse.utils.xml import XMLBinTypes as T, e_type


class Local(object):
    """
    Handle the Local request.

    This request handles most of the game specific requests.
    """

    # Methods
    SHOPINFO = "shopinfo"
    SHOPINFO_REGIST = "regist"

    DEMODATA = "demodata"
    DEMODATA_GET = "get"

    CARDUTIL = "cardutil"
    CARDUTIL_CHECK = "check"

    @classmethod
    def shopinfo(cls, req: ServiceRequest) -> etree:
        """
        Handle the shopinfo request

        Example Request:
            <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
                <shopinfo method="regist">
                    <shop>
                        <name __type="str">あ</name>
                        <pref __type="s8">31</pref>
                        <systemid __type="str">00010203040506070809</systemid>
                        <softwareid __type="str">012112345679</softwareid>
                        <hardwareid __type="str">010074D435AAD895</hardwareid>
                        <locationid __type="str">CA-123</locationid>
                        <testmode send="1">
                            <sound_options>
                                <volume_bgm __type="u8">20</volume_bgm>
                                <volume_se_myself __type="u8">20</volume_se_myself>
                            </sound_options>
                            <game_options>
                                <stand_alone>
                                    <difficulty_standard __type="u8">
                                        3
                                    </difficulty_standard>
                                    <max_stage_standard __type="u8">
                                        3
                                    </max_stage_standard>
                                    <long_music __type="u8">3</long_music>
                                </stand_alone>
                                <session>
                                    <game_joining_period __type="u8">
                                        15
                                    </game_joining_period>
                                </session>
                                <game_settings>
                                    <is_shop_close_on __type="u8">0</is_shop_close_on>
                                </game_settings>
                            </game_options>
                            <coin_options>
                                <coin_slot __type="u8">8</coin_slot>
                            </coin_options>
                            <bookkeeping>
                                <enable __type="u8">0</enable>
                            </bookkeeping>
                        </testmode>
                    </shop>
                </shopinfo>
            </call>

        Example Response:
            <response>
                <shopinfo>
                    <data>
                        <cabid __type="u32">1</cabid>
                        <locationid>nowhere</locationid>
                        <is_send __type="u8">1</is_send>
                    </data>
                </shopinfo>
            </response>
        """

        if req.method == cls.SHOPINFO_REGIST:
            response = E.response(
                E.shopinfo(
                    E.data(
                        E.cabid("1", e_type(T.u32)),
                        E.locationid("nowhere"),
                        E.is_send("1", e_type(T.u8)),
                    )
                )
            )
        else:
            raise Exception(
                "Not sure how to handle this shopinfo request. "
                f'method "{req.method}" is unknown for request: {req}'
            )

        return response

    @classmethod
    def demodata(cls, req: ServiceRequest) -> etree:
        """
        Handle the demodata request.

        # Example Request:
            <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
                <demodata method="get">
                    <shop>
                        <locationid __type="str">CA-123</locationid>
                    </shop>
                    <hitchart_nr __type="u16">100</hitchart_nr>
                </demodata>
            </call>

        # Example Response:
            <response>
                <demodata expire="600"/>
            </response>
        """
        # TODO: Figure out what this thing actually needs to send back

        if req.method == cls.DEMODATA_GET:
            response = E.response(E.demodata({"expire": "600"}))
        else:
            raise Exception(
                "Not sure how to handle this demodata request. "
                f'method "{req.method}" is unknown for request: {req}'
            )

        return response

    @classmethod
    def cardutil(cls, req: ServiceRequest) -> etree:
        """
        Handle the Cardutil request.

        # Example Request:
            <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
                <cardutil method="check">
                    <card no="1">
                        <refid __type="str">ADE0FE0B14AEAEFC</refid>
                        <uid __type="str">E0040100DE52896C</uid>
                    </card>
                </cardutil>
            </call>

        # Example Response:
            <response>
                <cardutil>
                    <card no="1" state="0">
                        <kind __type="s8")0</kind>
                    </card>
                </cardutil>
            </response>
        """
        # TODO: Figure out what this thing actually needs to send back

        if req.method == cls.CARDUTIL_CHECK:
            response = E.response(
                E.cardutil(E.card(E.kind("0", e_type(T.s8)), {"no": "1", "state": "0"}))
            )
        else:
            raise Exception(
                "Not sure how to handle this cardutil request. "
                f'method "{req.method}" is unknown for request: {req}'
            )

        return response
