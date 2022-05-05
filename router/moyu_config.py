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

QINGMING_DATE = datetime(2022, 4, 3, tzinfo=TZ)
QINGMING = """
 距离【清明】还有 {day} 天 {hour} 小时。清明节: 4 月 3 日 至 5 日放假调休, 共 3 天。4 月 2 日(星期六)上班。
"""

WUYI_DATE = datetime(2022, 5, 1, tzinfo=TZ)
WUYI = """
 距离【五一】还有 {day} 天 {hour} 小时。劳动节: 4 月 30 日 至 5 月 4 日放假调休, 共 5 天。4 月 24 日(星期日)、5 月 7 日(星期六)上班。
"""

DUANWU_DATE = datetime(2022, 6, 3, tzinfo=TZ)
DUANWU = """
 距离【端午】还有 {day} 天 {hour} 小时。端午节: 6 月 3 日 至 5 日放假, 共 3 天。
"""

ZHONGQIU_DATE = datetime(2022, 9, 10, tzinfo=TZ)
ZHONGQIU = """
 距离【中秋】还有 {day} 天 {hour} 小时。中秋节: 9 月 10 日 至 12 日放假, 共 3 天。
"""

GUOQING_DATE = datetime(2022, 10, 1, tzinfo=TZ)
GUOQING = """
 距离【国庆】还有 {day} 天 {hour} 小时。国庆节: 10 月1 日 至 7 日放假调休, 共 7 天。
"""

NEWYEAR_DATE = datetime(2022, 1, 1, tzinfo=TZ)
NEWYEAR = """
 距离【元旦】还有 {day} 天 {hour} 小时。
"""

SPRINGFEST_DATE = datetime(2023, 1, 22, tzinfo=TZ)
SPRINGFEST = """
 距离【春节】还有 {day} 天 {hour} 小时。
"""

FEST_MAP: Dict[datetime, str] = {
    QINGMING_DATE: QINGMING,
    WUYI_DATE: WUYI,
    DUANWU_DATE: DUANWU,
    ZHONGQIU_DATE: ZHONGQIU,
    GUOQING_DATE: GUOQING,
    NEWYEAR_DATE: NEWYEAR,
    SPRINGFEST_DATE: SPRINGFEST,
}


WEEK_DAYS = "一二三四五六日"
