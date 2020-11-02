import logging
from datetime import datetime

from lxml import etree
from lxml.builder import E

from v8_server import db
from v8_server.eamuse.services.services import ServiceRequest
from v8_server.eamuse.utils.crc import calculate_crc8
from v8_server.eamuse.utils.xml import XMLBinTypes as T, e_type
from v8_server.model.song import HitChart
from v8_server.model.user import User, UserAccount


logger = logging.getLogger(__name__)


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
    CARDUTIL_REGIST = "regist"

    GAMEINFO = "gameinfo"
    GAMEINFO_GET = "get"

    GAMEEND = "gameend"
    GAMEEND_REGIST = "regist"

    GAMEINFO = "gameinfo"
    GAMEINFO_GET = "get"

    GAMETOP = "gametop"
    GAMETOP_GET = "get"
    GAMETOP_GET_RIVAL = "get_rival"

    CUSTOMIZE = "customize"
    CUSTOMIZE_REGIST = "regist"

    ASSERT_REPORT = "assert_report"
    ASSERT_REPORT_REGIST = "regist"

    # Not sure about this one yet
    INCREMENT = "increment"

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

        Potentially this is just some initial demo data for initial boot/factory reset
        After this data, the game might keep track of all this stuff itself.

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
        dtfmt = "%Y-%m-%d %H:%M:%S%z"

        if req.method == cls.DEMODATA_GET:
            hitchart_number = int(req.xml[0].find("hitchart_nr").text)
            rank_data = HitChart.get_ranking(hitchart_number)

            response = E.response(
                E.demodata(
                    E.mode("0", e_type(T.u8)),  # Unknown what mode we need
                    E.hitchart(
                        E.start(datetime.now().strftime(dtfmt)),
                        E.end(datetime.now().strftime(dtfmt)),
                        *[
                            E.data(
                                E.musicid(str(x), e_type(T.s32)),
                                E.last1("0", e_type(T.s32)),
                            )
                            for x in rank_data
                        ],
                        {"nr": str(hitchart_number)},
                    ),
                    E.bossdata(  # No idea what this stuff means
                        E.division("14", e_type(T.u8)),  # Shows up as "Extra Lv X"
                        E.border("0 0 0 0 0 0 0 0 0", e_type(T.u8, count=9)),
                        E.extra_border("90", e_type(T.u8)),
                        E.bsc_encore_border("92", e_type(T.u8)),
                        E.adv_encore_border("93", e_type(T.u8)),
                        E.ext_encore_border("94", e_type(T.u8)),
                        E.bsc_premium_border("95", e_type(T.u8)),
                        E.adv_premium_border("95", e_type(T.u8)),
                        E.ext_premium_border("95", e_type(T.u8)),
                    ),
                    E.info(E.message("SenPi's Kickass Machine")),
                    E.assert_report_state("0", e_type(T.u8)),
                )
            )
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
                        <kind __type="s8">0</kind>
                    </card>
                </cardutil>
            </response>
        """
        # TODO: Figure out what this thing actually needs to send back

        if req.method == cls.CARDUTIL_CHECK:
            response = E.response(
                E.cardutil(E.card(E.kind("0", e_type(T.s8)), {"no": "1", "state": "0"}))
            )
        elif req.method == cls.CARDUTIL_REGIST:
            root = req.xml[0].find("data")
            refid = root.find("refid").text
            name = root.find("name").text
            chara = root.find("chara").text
            cardid = root.find("uid").text
            is_succession = root.find("is_succession").text

            user = User.from_refid(refid)
            if user is None:
                raise Exception("This user should theoretically exist here")
            if user.card.cardid != cardid:
                raise Exception(f"Card ID is incorrect: {user.card.cardid} != {cardid}")

            user_account = UserAccount(
                userid=user.userid,
                name=name,
                chara=int(chara),
                is_succession=True if is_succession == "1" else False,
            )
            db.session.add(user_account)
            db.session.commit()

            response = E.response(E.cardutil())
        else:
            raise Exception(
                "Not sure how to handle this cardutil request. "
                f'method "{req.method}" is unknown for request: {req}'
            )

        return response

    @classmethod
    def gameinfo(cls, req: ServiceRequest) -> etree:
        """
        Handle a Gameinfo request.

        Currently unsure how to handle this, so we just return a dummy object.

        # Example Request:
            <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
                <gameinfo method="get">
                    <shop>
                        <locationid __type="str">US-123</locationid>
                        <cabid __type="u32">1</cabid>
                    </shop>
                </gameinfo>
            </call>

        Example Response:
            <response>
                <gameinfo expire="600"/>
            </response>
        """
        if req.method == cls.GAMEINFO_GET:
            response = E.response(
                E.gameinfo(
                    E.mode("0", e_type(T.u8)),
                    E.free_music("262143", e_type(T.u32)),
                    E.key(E.musicid("-1", e_type(T.s32))),
                    E.limit_gdp("40000", e_type(T.u32)),
                    E.free_chara("1824", e_type(T.u32)),
                    E.tag(str(calculate_crc8(str(262143 + 1824))), e_type(T.u8)),
                    E.bossdata(
                        E.division("14", e_type(T.u8)),  # Shows up as "Extra Lv X"
                        E.border("0 0 0 0 0 0 0 0 0", e_type(T.u8, count=9)),
                        E.extra_border("90", e_type(T.u8)),
                        E.bsc_encore_border("92", e_type(T.u8)),
                        E.adv_encore_border("93", e_type(T.u8)),
                        E.ext_encore_border("94", e_type(T.u8)),
                        E.bsc_premium_border("95", e_type(T.u8)),
                        E.adv_premium_border("95", e_type(T.u8)),
                        E.ext_premium_border("95", e_type(T.u8)),
                    ),
                    E.battledata(
                        E.battle_music_level(
                            " ".join("0" * 13), e_type(T.u8, count=13)
                        ),
                        E.standard_skill(" ".join("0" * 13), e_type(T.s32, count=13)),
                        E.border_skill(" ".join("0" * 13), e_type(T.s32, count=13)),
                    ),
                    E.quest(
                        E.division("0", e_type(T.u8)),
                        E.border("0", e_type(T.u8)),
                        E.qdata(" ".join("0" * 26), e_type(T.u32, count=26)),
                        *[
                            E(f"play_{x}", " ".join("0" * 32), e_type(T.u32, count=32))
                            for x in range(0, 13)
                        ],
                        *[
                            E(f"clear_{x}", " ".join("0" * 32), e_type(T.u32, count=32))
                            for x in range(0, 13)
                        ],
                    ),
                    E.campaign(E.campaign("0", e_type(T.u8))),
                )
            )
        else:
            raise Exception(
                "Not sure how to handle this gameinfo request. "
                f'method "{req.method}" is unknown for request: {req}'
            )

        return response

    @classmethod
    def gametop(cls, req: ServiceRequest) -> etree:

        if req.method == cls.GAMETOP_GET:
            pass
        elif req.method == cls.GAMETOP_GET_RIVAL:
            pass
        else:
            raise Exception(
                "Not sure how to handle this gametop request. "
                f'method "{req.method}" is unknown for request: {req}'
            )

        return request

    @classmethod
    def gameend(cls, req: ServiceRequest) -> etree:
        """
        Handle a GameEnd request.

        For now just save the hitchart data
        """
        if req.method == cls.GAMEEND_REGIST:
            # Grab the hitchart data
            hc_root = req.xml[0].find("hitchart")

            for mid in hc_root.findall("musicid"):
                musicid = int(mid.text)
                hc = HitChart(musicid=musicid, playdate=datetime.now())
                logger.debug(f"Saving HitChart: {hc}")
                db.session.add(hc)
            db.session.commit()

            # Just send back a dummy object for now
            response = E.response(E.gameend())
        else:
            raise Exception(
                "Not sure how to handle this gameend request. "
                f'method "{req.method}" is unknown for request: {req}'
            )

        return response
