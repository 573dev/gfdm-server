import logging
from datetime import datetime

from lxml import etree
from lxml.builder import E

from v8_server import db
from v8_server.eamuse.services.services import ServiceRequest
from v8_server.eamuse.utils.crc import calculate_crc8
from v8_server.eamuse.xml.utils import XMLBinTypes as T, e_type, fill, get_xml_attrib
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
    def customize(cls, req: ServiceRequest) -> etree:
        if req.method == cls.CUSTOMIZE_REGIST:
            response = E.response(E.customize(E.player({"no": "1", "state": "2"})))
        else:
            raise Exception(
                "Not sure how to handle this customize request. "
                f'method "{req.method}" is unknown for request: {req}'
            )

        return response

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
            refid = req.xml[0].find("card/refid").text
            user = User.from_refid(refid)

            if user is None:
                response = E.response(
                    E.cardutil(
                        E.card(E.kind("0", e_type(T.s8)), {"no": "1", "state": "0"})
                    )
                )
            else:
                account = UserAccount.from_userid(user.userid)
                if account is None:
                    raise Exception("Account is none, wut?")

                response = E.response(
                    E.cardutil(
                        E.card(
                            E.kind("0", e_type(T.s8)),
                            E.name(account.name),
                            E.gdp("0", e_type(T.u32)),
                            E.skill("0", e_type(T.s32)),
                            E.all_skill("0", e_type(T.s32)),
                            E.chara(str(account.chara), e_type(T.u8)),
                            E.syogo(fill(2), e_type(T.s16, count=2)),
                            E.penalty("0", e_type(T.u8)),
                            {"no": "1", "state": "2"},
                        )
                    )
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
                        E.battle_music_level(fill(13), e_type(T.u8, count=13)),
                        E.standard_skill(fill(13), e_type(T.s32, count=13)),
                        E.border_skill(fill(13), e_type(T.s32, count=13)),
                    ),
                    E.quest(
                        E.division("0", e_type(T.u8)),
                        E.border("0", e_type(T.u8)),
                        E.qdata(fill(26), e_type(T.u32, count=26)),
                        *[
                            E(f"play_{x}", fill(32), e_type(T.u32, count=32))
                            for x in range(0, 13)
                        ],
                        *[
                            E(f"clear_{x}", fill(32), e_type(T.u32, count=32))
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
        refid = req.xml[0].find("player/refid").text
        # kind = int(req.xml[0].find("player/request/kind").text)
        # offset = int(req.xml[0].find("player/request/offset").text)
        # music_nr = int(req.xml[0].find("player/request/music_nr").text)

        user = User.from_refid(refid)
        if user is None:
            raise Exception(f"GameTop asking for invalid user with refid: {refid}")
        account = user.user_account

        if req.method == cls.GAMETOP_GET:
            response = E.response(
                E.gametop(
                    E.player(
                        E.player_type("0", e_type(T.u8)),
                        E.my_rival_id("0"),
                        E.mode("0", e_type(T.u8)),
                        E.syogo_list(fill(200, value="-1"), e_type(T.s16, count=200)),
                        E.badge_list(fill(200, value="-1"), e_type(T.s16, count=200)),
                        E.favorite_music(fill(20, value="-1"), e_type(T.s16, count=20)),
                        E.favorite_music_2(
                            fill(20, value="-1"), e_type(T.s16, count=20)
                        ),
                        E.favorite_music_3(
                            fill(20, value="-1"), e_type(T.s16, count=20)
                        ),
                        E.secret_music(fill(32), e_type(T.u16, count=32)),
                        E.style("2097152", e_type(T.u32)),
                        E.style_2("0", e_type(T.u32)),
                        E.shutter_list("0", e_type(T.u32)),
                        E.judge_logo_list("0", e_type(T.u32)),
                        E.skin_list("0", e_type(T.u32)),
                        E.movie_list("0", e_type(T.u32)),
                        E.attack_effect_list("0", e_type(T.u32)),
                        E.idle_screen("0", e_type(T.u32)),
                        E.chance_point("0", e_type(T.s32)),
                        E.failed_cnt("0", e_type(T.s32)),
                        E.secret_chara("0", e_type(T.u32)),
                        E.mode_beginner("0", e_type(T.u16)),
                        E.mode_standard("0", e_type(T.u16)),
                        E.mode_battle_global("0", e_type(T.u16)),
                        E.mode_battle_local("0", e_type(T.u16)),
                        E.mode_quest("0", e_type(T.u16)),
                        E.v3_skill("-1", e_type(T.s32)),
                        E.v4_skill("-1", e_type(T.s32)),
                        E.old_ver_skill("-1", e_type(T.s32)),
                        E.customize(
                            E.shutter("0", e_type(T.u8)),
                            E.info_level("0", e_type(T.u8)),
                            E.name_disp("0", e_type(T.u8)),
                            E.auto("0", e_type(T.u8)),
                            E.random("0", e_type(T.u8)),
                            E.judge_logo("0", e_type(T.u32)),
                            E.skin("0", e_type(T.u32)),
                            E.movie("0", e_type(T.u32)),
                            E.attack_effect("0", e_type(T.u32)),
                            E.layout("0", e_type(T.u8)),
                            E.target_skill("0", e_type(T.u8)),
                            E.comparison("0", e_type(T.u8)),
                            E.meter_custom(fill(3), e_type(T.u8, count=3)),
                        ),
                        E.tag(str(calculate_crc8("0")), e_type(T.u8)),
                        E.battledata(
                            E.bp("0", e_type(T.u32)),
                            E.battle_rate("0", e_type(T.s32)),
                            E.battle_class("0", e_type(T.u8)),
                            E.point("0", e_type(T.s16)),
                            E.rensyo("0", e_type(T.u16)),
                            E.win("0", e_type(T.u32)),
                            E.lose("0", e_type(T.u32)),
                            E.score_type("0", e_type(T.u8)),
                            E.strategy_item("0", e_type(T.s16)),
                            E.production_item("0", e_type(T.s16)),
                            E.draw("0", e_type(T.u32)),
                            E.max_class("0", e_type(T.u8)),
                            E.max_rensyo("0", e_type(T.u16)),
                            E.vip_rensyo("0", e_type(T.u16)),
                            E.max_defeat_skill("0", e_type(T.s32)),
                            E.max_defeat_battle_rate("0", e_type(T.s32)),
                            E.gold_star("0", e_type(T.u32)),
                            E.random_select("0", e_type(T.u32)),
                            E.enable_bonus_bp("0", e_type(T.u8)),
                            E.type_normal("0", e_type(T.u32)),
                            E.type_perfect("0", e_type(T.u32)),
                            E.type_combo("0", e_type(T.u32)),
                            E.area_id_list(fill(60), e_type(T.u8, count=60)),
                            E.area_win_list(fill(60), e_type(T.u32, count=60)),
                            E.area_lose_list(fill(60), e_type(T.u32, count=60)),
                            E.perfect("0", e_type(T.u32)),
                            E.great("0", e_type(T.u32)),
                            E.good("0", e_type(T.u32)),
                            E.poor("0", e_type(T.u32)),
                            E.miss("0", e_type(T.u32)),
                            E.history(
                                *[
                                    E.round(
                                        E.defeat_class("0", e_type(T.s8)),
                                        E.rival_type("0", e_type(T.s8)),
                                        E.name("0"),
                                        E.shopname("0"),
                                        E.chara_icon("0", e_type(T.u8)),
                                        E.pref("0", e_type(T.u8)),
                                        E.skill("0", e_type(T.s32)),
                                        E.battle_rate("0", e_type(T.s32)),
                                        E.syogo(fill(2), e_type(T.s16, count=2)),
                                        E.result("0", e_type(T.s8)),
                                        E.seqmode(fill(2), e_type(T.s8, count=2)),
                                        E.score_type(fill(2), e_type(T.s8, count=2)),
                                        E.musicid(fill(2), e_type(T.s32, count=2)),
                                        E.flags(fill(2), e_type(T.u32, count=2)),
                                        E.score_diff(fill(2), e_type(T.s32, count=2)),
                                        E.item(fill(2), e_type(T.s16, count=2)),
                                        E.select_type(fill(2), e_type(T.s8, count=2)),
                                        E.gold_star_hist("0", e_type(T.u8)),
                                        {"before": "0"},
                                    )
                                    for _ in range(0, 10)
                                ],
                            ),
                            E.music_hist(
                                *[
                                    E.round(
                                        E.point("0", e_type(T.s16)),
                                        E.my_select_musicid("0", e_type(T.s32)),
                                        E.my_select_result("0", e_type(T.s8)),
                                        E.rival_select_musicid("0", e_type(T.s32)),
                                        E.rival_select_result("0", e_type(T.s8)),
                                        {"before": "0"},
                                    )
                                    for _ in range(0, 20)
                                ],
                            ),
                        ),
                        E.battle_aniv(
                            E.get(
                                E.category_ver(fill(11), e_type(T.u16, count=11)),
                                E.category_genre(fill(11), e_type(T.u16, count=11)),
                            ),
                        ),
                        E.info(
                            E.mode("0", e_type(T.u32)),
                            E.boss("0", e_type(T.u32)),
                            E.battle_aniv("0", e_type(T.u32)),
                            E.free_music("0", e_type(T.u32)),
                            E.free_chara("0", e_type(T.u32)),
                            E.event("0", e_type(T.u32)),
                            E.battle_event("0", e_type(T.u32)),
                            E.champ("0", e_type(T.u32)),
                            E.item("0", e_type(T.u32)),
                            E.quest("0", e_type(T.u32)),
                            E.campaign("0", e_type(T.u32)),
                            E.gdp("0", e_type(T.u32)),
                            E.v7("0", e_type(T.u32)),
                        ),
                        E.quest(
                            E.quest_rank("0", e_type(T.u8)),
                            E.star("0", e_type(T.u32)),
                            E.fan("0", e_type(T.u64)),
                            E.qdata(fill(39), e_type(T.u32, count=39)),
                            E.test_data(fill(12), e_type(T.u32, count=12)),
                        ),
                        E.championship(E.playable(fill(4), e_type(T.s32, count=4))),
                        E.ranking(
                            E.skill_rank("0", e_type(T.s32)),
                        ),
                        E.rival_id_1("", e_type(T.str, count=1)),
                        E.rival_id_2("", e_type(T.str, count=1)),
                        E.rival_id_3("", e_type(T.str, count=1)),
                        E.standard({"nr": "0"}),
                        E.finish("1", e_type(T.u8)),
                        {"no": "1"},
                    )
                )
            )
        elif req.method == cls.GAMETOP_GET_RIVAL:
            response = E.response(
                E.gametop(
                    E.player(
                        E.pdata(
                            E.name(account.name),
                            E.chara(str(account.chara), e_type(T.u8)),
                            E.skill("0", e_type(T.s32)),
                            E.syogo(fill(2), e_type(T.s16, count=2)),
                            E.info_level("0", e_type(T.u8)),
                            E.bdata(
                                E.battle_rate("0", e_type(T.s32)),
                                E.battle_class("0", e_type(T.u8)),
                                E.point("0", e_type(T.s16)),
                                E.rensyo("0", e_type(T.u16)),
                                E.win("0", e_type(T.u32)),
                                E.lose("0", e_type(T.u32)),
                                E.draw("0", e_type(T.u32)),
                            ),
                            E.quest(
                                E.quest_rank("0", e_type(T.u8)),
                                E.star("0", e_type(T.u32)),
                                E.fan("0", e_type(T.u64)),
                                E.qdata(fill(13), e_type(T.u32, count=13)),
                                E.test_data(fill(12), e_type(T.u32, count=12)),
                            ),
                            {"rival_id": "0"},
                        ),
                        E.standard({"nr": "0"}),
                        E.finish("1", e_type(T.u8)),
                        {"no": "1"},
                    )
                )
            )
        else:
            raise Exception(
                "Not sure how to handle this gametop request. "
                f'method "{req.method}" is unknown for request: {req}'
            )

        return response

    @classmethod
    def gameend(cls, req: ServiceRequest) -> etree:
        """
        Handle a GameEnd request.

        For now just save the hitchart data
        """
        dtfmt = "%Y-%m-%d %H:%M:%S%z"

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
            gamemode = get_xml_attrib(req.xml[0].find("gamemode"), "game_mode")
            card = get_xml_attrib(req.xml[0].find("player"), "card")
            no = get_xml_attrib(req.xml[0].find("player"), "no")
            response = E.response(
                E.gameend(
                    E.gamemode({"mode": gamemode}),
                    E.player(
                        E.skill(
                            E.point("0", e_type(T.s32)),
                            E.rank("1", e_type(T.u32)),
                            E.total_nr("1", e_type(T.u32)),
                            E.all_point("0", e_type(T.s32)),
                            E.all_rank("1", e_type(T.u32)),
                            E.all_total_nr("1", e_type(T.u32)),
                        ),
                        E.registered_other_num("0", e_type(T.u32)),
                        E.xg_play_cnt("0", e_type(T.u32)),
                        E.play_cnt("0", e_type(T.u32)),
                        E.sess_cnt("0", e_type(T.u32)),
                        E.encore_play("0", e_type(T.u32)),
                        E.premium_play("0", e_type(T.u32)),
                        E.now_time(datetime.now().strftime(dtfmt)),
                        E.kikan_event("0", e_type(T.u32)),
                        E.vip_rensyo("0", e_type(T.u16)),
                        E.all_play_mode("0", e_type(T.u8)),
                        E.play_shop_num("0", e_type(T.u8)),
                        E.judge_perfect("0", e_type(T.u32)),
                        E.is_v5_goodplayer("0", e_type(T.u8)),
                        E.max_clear_difficulty("0", e_type(T.s8)),
                        E.max_fullcombo_difficulty("0", e_type(T.s8)),
                        E.max_excellent_difficulty("0", e_type(T.s8)),
                        E.rival_data(),
                        E.battledata(
                            E.bp("0", e_type(T.u32)),
                            E.battle_rate("0", e_type(T.s32)),
                            E.battle_class("0", e_type(T.u8)),
                            E.point("0", e_type(T.s16)),
                            E.rensyo("0", e_type(T.u16)),
                            E.win("0", e_type(T.u32)),
                            E.lose("0", e_type(T.u32)),
                            E.score_type("0", e_type(T.u8)),
                            E.strategy_item("0", e_type(T.s16)),
                            E.production_item("0", e_type(T.s16)),
                            E.draw("0", e_type(T.u32)),
                            E.max_class("0", e_type(T.u8)),
                            E.max_rensyo("0", e_type(T.u16)),
                            E.vip_rensyo("0", e_type(T.u16)),
                            E.max_defeat_skill("0", e_type(T.s32)),
                            E.max_defeat_battle_rate("0", e_type(T.s32)),
                            E.gold_star("0", e_type(T.u32)),
                            E.random_select("0", e_type(T.u32)),
                            E.type_normal("0", e_type(T.u32)),
                            E.type_perfect("0", e_type(T.u32)),
                            E.type_combo("0", e_type(T.u32)),
                            E.battle_aniv(
                                E.get(
                                    E.category_ver(fill(11), e_type(T.u16, count=11)),
                                    E.category_genre(fill(11), e_type(T.u16, count=11)),
                                ),
                            ),
                            E.area_id_list(fill(60), e_type(T.u8, count=60)),
                            E.area_win_list(fill(60), e_type(T.u32, count=60)),
                            E.area_lose_list(fill(60), e_type(T.u32, count=60)),
                            E.area_draw_list(fill(60), e_type(T.u32, count=60)),
                            E.perfect("0", e_type(T.u32)),
                            E.great("0", e_type(T.u32)),
                            E.good("0", e_type(T.u32)),
                            E.poor("0", e_type(T.u32)),
                            E.miss("0", e_type(T.u32)),
                            E.history(
                                *[
                                    E.round(
                                        E.defeat_class("0", e_type(T.s8)),
                                        E.rival_type("0", e_type(T.s8)),
                                        E.name("0"),
                                        E.shopname("0"),
                                        E.chara_icon("0", e_type(T.u8)),
                                        E.pref("0", e_type(T.u8)),
                                        E.skill("0", e_type(T.s32)),
                                        E.battle_rate("0", e_type(T.s32)),
                                        E.syogo(fill(2), e_type(T.s16, count=2)),
                                        E.result("0", e_type(T.s8)),
                                        E.seqmode(fill(2), e_type(T.s8, count=2)),
                                        E.score_type(fill(2), e_type(T.s8, count=2)),
                                        E.musicid(fill(2), e_type(T.s32, count=2)),
                                        E.flags(fill(2), e_type(T.u32, count=2)),
                                        E.score_diff(fill(2), e_type(T.s32, count=2)),
                                        E.item(fill(2), e_type(T.s16, count=2)),
                                        E.select_type(fill(2), e_type(T.s8, count=2)),
                                        E.gold_star_hist("0", e_type(T.u8)),
                                        {"before": "0"},
                                    )
                                    for _ in range(0, 10)
                                ],
                            ),
                            E.music_hist(
                                *[
                                    E.round(
                                        E.point("0", e_type(T.s16)),
                                        E.my_select_musicid("0", e_type(T.s32)),
                                        E.my_select_result("0", e_type(T.s8)),
                                        E.rival_select_musicid("0", e_type(T.s32)),
                                        E.rival_select_result("0", e_type(T.s8)),
                                        {"before": "0"},
                                    )
                                    for _ in range(0, 20)
                                ],
                            ),
                        ),
                        E.quest(
                            E.quest_rank("0", e_type(T.u8)),
                            E.star("0", e_type(T.u32)),
                            E.fan("0", e_type(T.u64)),
                            E.qdata(fill(39), e_type(T.u32, count=39)),
                        ),
                        E.championship(E.playable(fill(4), e_type(T.s32, count=4))),
                        {"card": card, "no": no},
                    ),
                )
            )
        else:
            raise Exception(
                "Not sure how to handle this gameend request. "
                f'method "{req.method}" is unknown for request: {req}'
            )

        return response
