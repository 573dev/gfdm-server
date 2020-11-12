import logging
from datetime import datetime

from lxml import etree

from v8_server import db
from v8_server.eamuse.services.services import ServiceRequest
from v8_server.eamuse.xml.utils import get_xml_attrib, load_xml_template
from v8_server.model.song import HitChart
from v8_server.utils.convert import int_to_bool as itob


logger = logging.getLogger(__name__)


class Gamemode(object):
    """
    Gameend.Regist.Gamemode object
    """

    def __init__(self, root: etree) -> None:
        self.mode = get_xml_attrib(root, "mode")

    def __repr__(self) -> str:
        return f'Gamemode<mode = "{self.mode}">'


class Shop(object):
    """
    Gameend.Regist.Shop object
    """

    def __init__(self, root: etree) -> None:
        self.cabid = int(root.find("cabid").text)

    def __repr__(self) -> str:
        return f"Shop<cabid = {self.cabid}>"


class Hitchart(object):
    """
    Gameend.Regist.Hitchart object
    """

    def __init__(self, root: etree) -> None:
        self.musicids = [int(x.text) for x in root.findall("musicid")]

    def __repr__(self) -> str:
        return f"Hitchart<musicids = {self.musicids}>"


class Stage(object):
    """
    Gameend.Regist.Modedata.Stage object
    """

    def __init__(self, root: etree) -> None:
        self.no = int(root.find("no").text)
        self.musicid = int(root.find("musicid").text)
        self.newmusic = itob(int(root.find("newmusic").text))
        self.longmusic = itob(int(root.find("longmusic").text))
        self.kind = int(root.find("kind").text)

    def __repr__(self) -> str:
        return (
            f"Stage<no = {self.no}, musicid = {self.musicid}, "
            f"newmusic = {self.newmusic}, longmusic = {self.longmusic}, "
            f"kind = {self.kind}>"
        )


class Modedata(object):
    """
    Gameend.Regist.Modedata object
    """

    def __init__(self, root: etree) -> None:
        self.mode = get_xml_attrib(root, "mode")
        self.stages = [Stage(x) for x in root.findall("stage")]
        self.session = int(root.find("session").text)

    def __repr__(self) -> str:
        return (
            f'Modedata<mode = "{self.mode}", stages = {self.stages}, '
            f"session = {self.session}>"
        )


class Info(object):
    """
    Gameend.Regist.Player.Playerinfo.Info object
    """

    def __init__(self, root: etree) -> None:
        self.mode = int(root.find("mode").text)
        self.boss = int(root.find("boss").text)
        self.battle_aniv = int(root.find("battle_aniv").text)  # Possible Bool?
        self.free_music = int(root.find("free_music").text)
        self.free_chara = int(root.find("free_chara").text)
        self.event = int(root.find("event").text)
        self.battle_event = int(root.find("battle_event").text)
        self.champ = int(root.find("champ").text)
        self.item = int(root.find("item").text)
        self.quest = int(root.find("quest").text)
        self.campaign = int(root.find("campaign").text)
        self.gdp = int(root.find("gdp").text)
        self.v7 = int(root.find("v7").text)  # Possible Bool?
        self.champ_result = [int(x) for x in root.find("champ_result").text.split()]

    def __repr__(self) -> str:
        return (
            f"Info<mode = {self.mode}, boss = {self.boss}, "
            f"battle_aniv = {self.battle_aniv}, free_music = {self.free_music}, "
            f"free_chara = {self.free_chara}, event = {self.event}, "
            f"battle_event = {self.battle_event}, champ = {self.champ}, "
            f"item = {self.item}, quest = {self.quest}, campaign = {self.campaign}, "
            f"gdp = {self.gdp}, v7 = {self.v7}, champ_result = {self.champ_result}>"
        )


class Customize(object):
    """
    Gameend.Regist.Player.Playerinfo.Customize object

    This is potentially the mod (speed mods, dark, auto bass, etc) data
    """

    def __init__(self, root: etree) -> None:
        self.shutter = int(root.find("shutter").text)
        self.info_level = int(root.find("info_level").text)
        self.name_disp = int(root.find("name_disp").text)  # Possible Bool?
        self.auto = int(root.find("auto").text)
        self.random = int(root.find("random").text)
        self.judge_logo = int(root.find("judge_logo").text)
        self.skin = int(root.find("skin").text)
        self.movie = int(root.find("movie").text)
        self.attack_effect = int(root.find("attack_effect").text)
        self.layout = int(root.find("layout").text)
        self.target_skill = int(root.find("target_skill").text)
        self.comparison = int(root.find("comparison").text)
        self.meter_custom = [int(x) for x in root.find("meter_custom").text.split()]

    def __repr__(self) -> str:
        return (
            f"Customize<shutter = {self.shutter}, info_level = {self.info_level}, "
            f"name_disp = {self.name_disp}, auto = {self.auto}, "
            f"random = {self.random}, judge_logo = {self.judge_logo}, "
            f"skin = {self.skin}, movie = {self.movie}, "
            f"attack_effect = {self.attack_effect}, layout = {self.layout}, "
            f"target_skill = {self.target_skill}, comparison = {self.comparison}, "
            f"meter_custom = {self.meter_custom}>"
        )


class Playerinfo(object):
    """
    Gameend.Regist.Player.Playerinfo object
    """

    def __init__(self, root: etree) -> None:
        self.refid = root.find("refid").text
        self.gdp = int(root.find("gdp").text)
        self.bad_play_kind = int(root.find("bad_play_kind").text)
        self.total_skill_point = int(root.find("total_skill_point").text)
        self.styles = int(root.find("styles").text)
        self.styles_2 = int(root.find("styles_2").text)
        self.secret_music = [int(x) for x in root.find("secret_music").text.split()]
        self.chara = int(root.find("chara").text)
        self.secret_chara = int(root.find("secret_chara").text)
        self.syogo = [int(x) for x in root.find("syogo").text.split()]
        self.shutter_list = int(root.find("shutter_list").text)
        self.judge_logo_list = int(root.find("judge_logo_list").text)
        self.skin_list = int(root.find("skin_list").text)
        self.movie_list = int(root.find("movie_list").text)
        self.attack_effect_list = int(root.find("attack_effect_list").text)
        self.idle_screen = int(root.find("idle_screen").text)
        self.chance_point = int(root.find("chance_point").text)
        self.failed_cnt = int(root.find("failed_cnt").text)
        self.perfect = int(root.find("perfect").text)
        self.great = int(root.find("great").text)
        self.good = int(root.find("good").text)
        self.poor = int(root.find("poor").text)
        self.miss = int(root.find("miss").text)
        self.time = int(root.find("time").text)
        self.exc_clear_num = int(root.find("exc_clear_num").text)
        self.full_clear_num = int(root.find("full_clear_num").text)
        self.max_clear_difficulty = int(root.find("max_clear_difficulty").text)
        self.max_fullcombo_difficulty = int(root.find("max_fullcombo_difficulty").text)
        self.max_excellent_difficulty = int(root.find("max_excellent_difficulty").text)
        self.champ_group = int(root.find("champ_group").text)
        self.champ_kind = int(root.find("champ_kind").text)
        self.musicid = [int(x) for x in root.find("musicid").text.split()]
        self.object_musicid = [int(x) for x in root.find("object_musicid").text.split()]
        self.seqmode = [int(x) for x in root.find("seqmode").text.split()]
        self.flags = [int(x) for x in root.find("flags").text.split()]
        self.score = [int(x) for x in root.find("score").text.split()]
        self.point = [int(x) for x in root.find("point").text.split()]
        self.info = Info(root.find("info"))
        self.customize = Customize(root.find("customize"))
        # There seems to be another `perfect` here for some reason
        self.bp = int(root.find("bp").text)
        self.reserv_item_list = [
            int(x) for x in root.find("reserv_item_list").text.split()
        ]
        self.rival_id_1 = root.find("rival_id_1").text
        self.rival_id_2 = root.find("rival_id_2").text
        self.rival_id_3 = root.find("rival_id_3").text

    def __repr__(self) -> str:
        return (
            f'Playerinfo<refid = "{self.refid}", gdp = {self.gdp}, '
            f"bad_play_kind = {self.bad_play_kind}, "
            f"total_skill_point = {self.total_skill_point}, "
            f"styles = {self.styles}, styles_2 = {self.styles_2}, "
            f"secret_music = {self.secret_music}, chara = {self.chara}, "
            f"secret_chara = {self.secret_chara}, syogo = {self.syogo}, "
            f"shutter_list = {self.shutter_list}, "
            f"judge_logo_list = {self.judge_logo_list}, "
            f"skin_list = {self.skin_list}, movie_list = {self.movie_list}, "
            f"attack_effect_list = {self.attack_effect_list}, "
            f"idle_screen = {self.idle_screen}, "
            f"chance_point = {self.chance_point}, failed_cnt = {self.failed_cnt}, "
            f"perfect = {self.perfect}, great = {self.great}, good = {self.good}, "
            f"poor = {self.poor}, miss = {self.miss}, time = {self.time}, "
            f"exc_clear_num = {self.exc_clear_num}, "
            f"full_clear_num = {self.full_clear_num}, "
            f"max_clear_difficulty = {self.max_clear_difficulty}, "
            f"max_fullcombo_difficulty = {self.max_fullcombo_difficulty}, "
            f"max_excellent_difficulty = {self.max_excellent_difficulty}, "
            f"champ_group = {self.champ_group}, champ_kind = {self.champ_kind}, "
            f"musicid = {self.musicid}, object_musicid = {self.object_musicid}, "
            f"seqmode = {self.seqmode}, flags = {self.flags}, "
            f"score = {self.score}, point = {self.point}, info = {self.info}, "
            f"customize = {self.customize}, bp = {self.bp}, "
            f"reserv_item_list = {self.reserv_item_list}, "
            f'rival_id_1 = "{self.rival_id_1}", rival_id_2 = "{self.rival_id_2}", '
            f'rival_id_3 = "{self.rival_id_3}">'
        )


class Playdata(object):
    """
    Gameend.Regist.Player.Playdata object
    """

    def __init__(self, root: etree) -> None:
        self.no = int(root.find("no").text)
        self.seqmode = int(root.find("seqmode").text)
        self.clear = int(root.find("clear").text)
        self.auto_clear = int(root.find("auto_clear").text)
        self.score = int(root.find("score").text)
        self.flags = int(root.find("flags").text)
        self.fullcombo = int(root.find("fullcombo").text)
        self.excellent = int(root.find("excellent").text)
        self.combo = int(root.find("combo").text)
        self.skill_point = int(root.find("skill_point").text)
        self.skill_perc = int(root.find("skill_perc").text)
        self.result_rank = int(root.find("result_rank").text)
        self.difficulty = int(root.find("difficulty").text)
        self.combo_rate = int(root.find("combo_rate").text)
        self.perfect_rate = int(root.find("perfect_rate").text)

    def __repr__(self) -> str:
        return (
            f"Playdata<no = {self.no}, seqmode = {self.seqmode}, clear = {self.clear}, "
            f"auto_clear = {self.auto_clear}, score = {self.score}, "
            f"flag = {self.flags}, fullcombo = {self.fullcombo}, "
            f"excellent = {self.excellent}, combo = {self.combo}, "
            f"skill_point = {self.skill_point}, skill_perc = {self.skill_perc}, "
            f"result_rank = {self.result_rank}, difficulty = {self.difficulty}, "
            f"combo_rate = {self.combo_rate}, perfect_rate = {self.perfect_rate}>"
        )


class Player(object):
    """
    Gameend.Regist.Player object
    """

    def __init__(self, root: etree) -> None:
        self.card = get_xml_attrib(root, "card")
        self.no = int(get_xml_attrib(root, "no"))
        self.playerinfo = Playerinfo(root.find("playerinfo"))
        self.playdata = [Playdata(x) for x in root.findall("playdata")]

    def __repr__(self) -> str:
        return (
            f'Player<card = "{self.card}", no = {self.no}, '
            f"playerinfo = {self.playerinfo}, playdata = {self.playdata}>"
        )


class Regist(object):
    """
    Handle the Gameend Regist request.

    <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
        <gameend method="regist">
            <gamemode mode="game_mode"/>
            <shop>
                <cabid __type="u32">1</cabid>
            </shop>
            <hitchart>
                <musicid __type="s32">1849</musicid>
            </hitchart>
            <modedata mode="standard">
                <stage>
                    <no __type="u8">1</no>
                    <musicid __type="s32">1849</musicid>
                    <newmusic __type="u8">1</newmusic>
                    <longmusic __type="u8">0</longmusic>
                    <kind __type="u8">0</kind>
                </stage>
                <session __type="u8">0</session>
            </modedata>
            <player card="use" no="1">
                <playerinfo>
                    <refid __type="str">E9D2DD02072F05C5</refid>
                    <gdp __type="u32">900</gdp>
                    <bad_play_kind __type="s32">0</bad_play_kind>
                    <total_skill_point __type="s32">0</total_skill_point>
                    <styles __type="u32">2097152</styles>
                    <styles_2 __type="u32">0</styles_2>
                    <secret_music __type="u16" __count="32">
                        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
                    </secret_music>
                    <chara __type="u8">0</chara>
                    <secret_chara __type="u32">1824</secret_chara>
                    <syogo __type="s16" __count="2">0 0</syogo>
                    <shutter_list __type="u32">0</shutter_list>
                    <judge_logo_list __type="u32">0</judge_logo_list>
                    <skin_list __type="u32">0</skin_list>
                    <movie_list __type="u32">0</movie_list>
                    <attack_effect_list __type="u32">0</attack_effect_list>
                    <idle_screen __type="u32">0</idle_screen>
                    <chance_point __type="s32">0</chance_point>
                    <failed_cnt __type="s32">0</failed_cnt>
                    <perfect __type="u32">0</perfect>
                    <great __type="u32">0</great>
                    <good __type="u32">0</good>
                    <poor __type="u32">0</poor>
                    <miss __type="u32">120</miss>
                    <time __type="u32">222</time>
                    <exc_clear_num __type="u32">0</exc_clear_num>
                    <full_clear_num __type="u32">0</full_clear_num>
                    <max_clear_difficulty __type="s8">0</max_clear_difficulty>
                    <max_fullcombo_difficulty __type="s8">0</max_fullcombo_difficulty>
                    <max_excellent_difficulty __type="s8">0</max_excellent_difficulty>
                    <champ_group __type="u8">0</champ_group>
                    <champ_kind __type="u8">0</champ_kind>
                    <musicid __type="s32" __count="6">0 0 0 0 0 0</musicid>
                    <object_musicid __type="s32" __count="6">
                        0 0 0 0 0 0
                    </object_musicid>
                    <seqmode __type="s8" __count="6">0 0 0 0 0 0</seqmode>
                    <flags __type="u32" __count="6">0 0 0 0 0 0</flags>
                    <score __type="u32" __count="6">0 0 0 0 0 0</score>
                    <point __type="u32" __count="6">0 0 0 0 0 0</point>
                    <info>
                        <mode __type="u32">0</mode>
                        <boss __type="u32">0</boss>
                        <battle_aniv __type="u32">0</battle_aniv>
                        <free_music __type="u32">0</free_music>
                        <free_chara __type="u32">0</free_chara>
                        <event __type="u32">0</event>
                        <battle_event __type="u32">0</battle_event>
                        <champ __type="u32">0</champ>
                        <item __type="u32">0</item>
                        <quest __type="u32">0</quest>
                        <campaign __type="u32">0</campaign>
                        <gdp __type="u32">0</gdp>
                        <v7 __type="u32">0</v7>
                        <champ_result __type="u32" __count="2">0 0</champ_result>
                    </info>
                    <customize>
                        <shutter __type="u8">0</shutter>
                        <info_level __type="u8">0</info_level>
                        <name_disp __type="u8">0</name_disp>
                        <auto __type="u8">0</auto>
                        <random __type="u8">0</random>
                        <judge_logo __type="u32">0</judge_logo>
                        <skin __type="u32">0</skin>
                        <movie __type="u32">0</movie>
                        <attack_effect __type="u32">0</attack_effect>
                        <layout __type="u8">0</layout>
                        <target_skill __type="u8">0</target_skill>
                        <comparison __type="u8">0</comparison>
                        <meter_custom __type="u8" __count="3">0 0 0</meter_custom>
                    </customize>
                    <perfect __type="u32">0</perfect>
                    <bp __type="u32">0</bp>
                    <reserv_item_list __type="s16" __count="200">
                        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
                        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
                        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
                        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
                        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
                        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
                        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
                        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
                    </reserv_item_list>
                    <rival_id_1 __type="str"></rival_id_1>
                    <rival_id_2 __type="str"></rival_id_2>
                    <rival_id_3 __type="str"></rival_id_3>
                </playerinfo>
                <playdata>
                    <no __type="u8">1</no>
                    <seqmode __type="s8">1</seqmode>
                    <clear __type="u8">0</clear>
                    <auto_clear __type="u8">0</auto_clear>
                    <score __type="u32">0</score>
                    <flags __type="u32">0</flags>
                    <fullcombo __type="u8">0</fullcombo>
                    <excellent __type="u8">0</excellent>
                    <combo __type="u32">0</combo>
                    <skill_point __type="s32">0</skill_point>
                    <skill_perc __type="s32">-1</skill_perc>
                    <result_rank __type="s8">0</result_rank>
                    <difficulty __type="s8">11</difficulty>
                    <combo_rate __type="s8">0</combo_rate>
                    <perfect_rate __type="s8">0</perfect_rate>
                </playdata>
            </player>
        </gameend>
    </call>
    """

    DT_FMT = "%Y-%m-%d %H:%M:%S%z"

    def __init__(self, req: ServiceRequest) -> None:
        self.gamemode = Gamemode(req.xml[0].find("gamemode"))
        self.shop = Shop(req.xml[0].find("shop"))
        self.hitchart = Hitchart(req.xml[0].find("hitchart"))
        self.modedata = Modedata(req.xml[0].find("modedata"))
        self.player = Player(req.xml[0].find("player"))

    def __repr__(self) -> str:
        return (
            f"Gameend.Regist<gamemode = {self.gamemode}, shop = {self.shop}, "
            f"hitchart = {self.hitchart}, modedata = {self.modedata}, "
            f"player = {self.player}>"
        )

    def response(self) -> etree:
        for musicid in self.hitchart.musicids:
            hc = HitChart(musicid=musicid, playdate=datetime.now())
            logger.debug(f"Saving HitChart: {hc}")
            db.session.add(hc)
        db.session.commit()

        # Just send back a dummy object for now
        now_time = datetime.now().strftime(self.DT_FMT)

        # Generate history rounds (blank for now)
        history_rounds = ""
        for _ in range(0, 10):
            history_rounds += etree.tostring(
                load_xml_template("gameend", "regist.history.round")
            ).decode("UTF-8")

        music_hist_rounds = ""
        for _ in range(0, 20):
            music_hist_rounds += etree.tostring(
                load_xml_template("gameend", "regist.music_hist.round")
            ).decode("UTF-8")

        args = {
            "gamemode": self.gamemode.mode,
            "player_card": self.player.card,
            "player_no": self.player.no,
            "now_time": now_time,
            "history_rounds": history_rounds,
            "music_hist_rounds": music_hist_rounds,
        }

        return load_xml_template("gameend", "regist", args)
