from datetime import timedelta, timezone, datetime
from typing import Dict


TZ = timezone(timedelta(hours=8))


MO_YU_TEMPLATE = """
【摸鱼办】提醒您:

 今天是 {year}年{month}月{day}日, 星期{weekday}
 你好, 摸鱼人！工作再忙, 一定不要忘记摸鱼哦！
 有事没事起身去茶水间, 去厕所, 去走廊走走, 去找同事聊聊八卦别老在工位上坐着, 钱是老板的但命是自己的。

 温馨提示:
 {year}年 已经过去 {passdays} 天 {passhours} 小时
 距离【月底发工资】: {salaryday1} 天
 距离【05号发工资】: {salaryday5} 天
 距离【10号发工资】: {salaryday10} 天
 距离【15号发工资】: {salaryday15} 天
 距离【20号发工资】: {salaryday20} 天
 距离【周六】还有 {day_to_weekend} 天
"""

MO_YU_TEMPLATE_DAY_N = """
【摸鱼办】提醒您:

 今天是 {year}年{month}月{day}日, 星期{weekday}
 你好, 摸鱼人！工作再忙, 一定不要忘记摸鱼哦！
 有事没事起身去茶水间, 去厕所, 去走廊走走, 去找同事聊聊八卦别老在工位上坐着, 钱是老板的但命是自己的。

 温馨提示:
 {year}年 已经过去 {passdays} 天 {passhours} 小时
 距离【 {salaryday} 号发工资】: {salarydayn} 天
 距离【周六】还有 {day_to_weekend} 天
"""

NEWYEAR_DATE = datetime(2023, 12, 30, tzinfo=TZ)
NEWYEAR = """
 距离【元旦】还有 {day} 天 {hour} 小时。2023年12月30日至2024年1月1日放假调休, 共3天。
"""

SPRINGFEST_DATE = datetime(2024, 2, 10, tzinfo=TZ)
SPRINGFEST = """
 距离【春节】还有 {day} 天 {hour} 小时。2月10日至2月17日放假调休, 共8天。2月4日(星期日)、2月18日(星期日)上班。
"""

QINGMING_DATE = datetime(2024, 4, 4, tzinfo=TZ)
QINGMING = """
 距离【清明】还有 {day} 天 {hour} 小时。4月4日至4月6日放假调休, 共3天。4月7日(星期日)上班。
"""

WUYI_DATE = datetime(2024, 5, 1, tzinfo=TZ)
WUYI = """
 距离【五一】还有 {day} 天 {hour} 小时。5月1日至5月5日放假调休, 共5天。4月28日(星期日)、5月11日(星期六)上班。
"""

DUANWU_DATE = datetime(2024, 6, 10, tzinfo=TZ)
DUANWU = """
 距离【端午】还有 {day} 天 {hour} 小时。6月10日放假, 共1天。
"""

ZHONGQIU_DATE = datetime(2024, 9, 17, tzinfo=TZ)
ZHONGQIU = """
 距离【中秋】还有 {day} 天 {hour} 小时。9月15日至9月17日放假调休, 共3天。9月14日(星期六)上班。
"""

GUOQING_DATE = datetime(2024, 10, 1, tzinfo=TZ)
GUOQING = """
 距离【国庆】还有 {day} 天 {hour} 小时。10月1日至10月7日放假调休, 共7天。9月29日(星期日)、10月12日(星期六)上班。
"""


FEST_MAP: Dict[datetime, str] = {
    NEWYEAR_DATE: NEWYEAR,
    SPRINGFEST_DATE: SPRINGFEST,
    QINGMING_DATE: QINGMING,
    WUYI_DATE: WUYI,
    DUANWU_DATE: DUANWU,
    ZHONGQIU_DATE: ZHONGQIU,
    GUOQING_DATE: GUOQING,
}


WEEK_DAYS = "一二三四五六日"
