# -*- coding: utf-8 -*-
# KOPIS + 멜론티켓 K-Pop 콘서트 수집 -> concerts.json

import requests
import xml.etree.ElementTree as ET
import json
import re
import time
from datetime import datetime, timedelta

import os
SERVICE_KEY = os.environ.get("KOPIS_SERVICE_KEY", "78bdffdd1a6346069f7c5f8b0836b14c")
GENRE_POP = "CCCD"
URL = "http://www.kopis.or.kr/openApi/restful/pblprfr"
MONTHS = 6

CASE_SENSITIVE = {"god"}

LARGE_VENUE_KEYWORDS = [
    "올림픽공원", "잠실", "고척", "아레나", "스타디움", "체육관",
    "월드컵", "아시아드", "인스파이어", "BEXCO", "벡스코",
    "KINTEX", "킨텍스", "코엑스", "컨벤시아", "사직", "문학",
    "대구스타디움", "광주월드컵", "SK핸드볼", "부산항국제전시컨벤션센터",
]

SMALL_VENUE_OK = {"포레스텔라", "성시경", "god"}

EXCLUDE_KEYWORDS = [
    "팬미팅", "팬 미팅", "팬콘", "팬파티",
    "FAN MEETING", "FANMEETING", "FANCON", "FAN CON", "FAN PARTY", "FANPARTY",
    "사인회", "쇼케이스", "SHOWCASE",
]

MELON_URL = "https://ticket.melon.com/performance/ajax/prodList.json"
MELON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9",
}

ARTISTS = {
    "B1A4": ["B1A4"],
    "EXID": ["EXID", "이엑스아이디"],
    "ITZY": ["ITZY", "있지"],
    "NCT": ["NCT", "엔시티"],
    "SF9": ["SF9", "에스에프나인"],
    "갓세븐": ["GOT7", "갓세븐"],
    "뉴이스트": ["NU'EST", "뉴이스트"],
    "뉴진스": ["NewJeans", "뉴진스"],
    "더보이즈": ["THE BOYZ", "더보이즈"],
    "데이식스": ["DAY6", "데이식스"],
    "라이즈": ["RIIZE", "라이즈"],
    "러블리즈": ["Lovelyz", "러블리즈"],
    "레드벨벳": ["Red Velvet", "레드벨벳"],
    "르세라핌": ["LE SSERAFIM", "르세라핌"],
    "마마무": ["MAMAMOO", "마마무"],
    "몬스타엑스": ["MONSTA X", "몬스타엑스"],
    "미래소년": ["MIRAE", "미래소년"],
    "방탄소년단": ["BTS", "방탄소년단"],
    "베이비몬스터": ["BABYMONSTER", "베이비몬스터"],
    "보이넥스트도어": ["BOYNEXTDOOR", "보이넥스트도어"],
    "브레이브걸스": ["Brave Girls", "브레이브걸스"],
    "블랙핑크": ["BLACKPINK", "블랙핑크"],
    "비투비": ["BTOB", "비투비"],
    "빅스": ["VIXX", "빅스"],
    "세븐틴": ["SEVENTEEN", "세븐틴"],
    "스테이씨": ["STAYC", "스테이씨"],
    "스트레이 키즈": ["Stray Kids", "스트레이 키즈", "스트레이키즈"],
    "시크릿넘버": ["SECRET NUMBER", "시크릿넘버"],
    "싸이커스": ["Xikers", "싸이커스"],
    "아스트로": ["ASTRO", "아스트로"],
    "아이들": ["(G)I-DLE", "(여자)아이들"],
    "아이브": ["IVE", "아이브"],
    "아이콘": ["iKON", "아이콘"],
    "아일릿": ["ILLIT", "아일릿"],
    "에스파": ["aespa", "에스파"],
    "에이티즈": ["ATEEZ", "에이티즈"],
    "에이핑크": ["Apink", "에이핑크"],
    "엑소": ["EXO", "엑소"],
    "엑스디너리 히어로즈": ["Xdinary Heroes", "엑스디너리"],
    "엔믹스": ["NMIXX", "엔믹스"],
    "엔플라잉": ["N.Flying", "엔플라잉"],
    "엔하이픈": ["ENHYPEN", "엔하이픈"],
    "여자친구": ["GFRIEND", "여자친구"],
    "오마이걸": ["OH MY GIRL", "오마이걸"],
    "우주소녀": ["WJSN", "우주소녀"],
    "위너": ["WINNER", "위너"],
    "위클리": ["Weeekly", "위클리"],
    "유니스": ["UNIS", "유니스"],
    "이달의 소녀": ["LOONA", "이달의 소녀", "이달의소녀"],
    "이펙스": ["EPEX", "이펙스"],
    "인피니트": ["INFINITE", "인피니트"],
    "저스트비": ["JUST B", "저스트비"],
    "제로베이스원": ["ZEROBASEONE", "제로베이스원", "ZB1"],
    "케플러": ["Kep1er", "케플러"],
    "클라씨": ["CLASS:y", "클라씨"],
    "키스오브라이프": ["KISS OF LIFE", "키스오브라이프"],
    "템페스트": ["TEMPEST", "템페스트"],
    "투모로우바이투게더": ["TXT", "투모로우바이투게더", "TOMORROW X TOGETHER"],
    "투어스": ["TWS", "투어스"],
    "트라이비": ["TRI.BE", "트라이비"],
    "트레저": ["TREASURE", "트레저"],
    "트리플에스": ["tripleS", "트리플에스"],
    "트와이스": ["TWICE", "트와이스"],
    "틴탑": ["TEEN TOP", "틴탑"],
    "퍼플키스": ["PURPLE KISS", "퍼플키스"],
    "펜타곤": ["PENTAGON", "펜타곤"],
    "플레이브": ["PLAVE", "플레이브"],
    "피원하모니": ["P1Harmony", "피원하모니"],
    "피프티피프티": ["FIFTY FIFTY", "피프티피프티"],
    "샤이니": ["SHINee", "샤이니"],
    "소녀시대": ["Girls' Generation", "소녀시대", "SNSD"],
    "슈퍼주니어": ["SUPER JUNIOR", "슈퍼주니어"],
    "동방신기": ["TVXQ", "동방신기"],
    "빅뱅": ["BIGBANG", "빅뱅"],
    "2PM": ["2PM"],
    "하이라이트": ["Highlight", "하이라이트"],
    "god": ["god", "지오디"],
    "카라": ["KARA"],
    "씨엔블루": ["CNBLUE", "씨엔블루"],
    "FT아일랜드": ["FTISLAND", "FT아일랜드", "FT ISLAND"],
    "브라운아이드걸스": ["Brown Eyed Girls", "브라운아이드걸스"],
    "싸이": ["PSY", "싸이"],
    "포레스텔라": ["Forestella", "포레스텔라"],
    "성시경": ["성시경"],
}

DEBUG_CHECK = ["보이넥스트도어", "BOYNEXTDOOR", "투어스", "TWS", "세븐틴", "SEVENTEEN", "엔하이픈", "ENHYPEN"]


def fetch_period(stdate, eddate):
    results = []
    cpage = 1
    while True:
        params = {
            "service": SERVICE_KEY,
            "stdate": stdate, "eddate": eddate,
            "cpage": str(cpage), "rows": "100",
            "shcate": GENRE_POP,
        }
        try:
            resp = requests.get(URL, params=params, timeout=20)
            resp.encoding = "utf-8"
            root = ET.fromstring(resp.text)
        except Exception:
            break
        dbs = root.findall("db")
        if not dbs:
            break
        for db in dbs:
            results.append({
                "id": db.findtext("mt20id", ""),
                "prfnm": db.findtext("prfnm", ""),
                "from": db.findtext("prfpdfrom", ""),
                "to": db.findtext("prfpdto", ""),
                "fclt": db.findtext("fcltynm", ""),
                "area": db.findtext("area", ""),
            })
        if len(dbs) < 100:
            break
        cpage += 1
        time.sleep(0.2)
    return results


def collect_all():
    today = datetime.now()
    end = today + timedelta(days=MONTHS * 30)
    all_perf = {}
    cur = today
    while cur < end:
        chunk_end = min(cur + timedelta(days=9), end)
        for p in fetch_period(cur.strftime("%Y%m%d"), chunk_end.strftime("%Y%m%d")):
            all_perf[p["id"]] = p
        cur = chunk_end + timedelta(days=1)
    return list(all_perf.values())


def collect_melon():
    """멜론티켓 아이돌 콘서트 수집"""
    results = []
    params = {
        "commCode": "",
        "sortType": "SORT_DEFAULT",
        "perfGenreCode": "GENRE_CON_IDOL",
        "perfThemeCode": "",
        "filterCode": "FILTER_ALL",
        "v": "1",
    }
    try:
        resp = requests.get(MELON_URL, headers=MELON_HEADERS, params=params, timeout=15)
        data = resp.json()
        items = data.get("data", [])
        for item in items:
            period = item.get("periodInfo", "")
            # "2026.05.29 - 2026.05.31" → "2026-05-29~2026-05-31"
            parts = [p.strip().replace(".", "-") for p in period.split(" - ")]
            date_str = parts[0] if len(parts) == 1 else (parts[0] if parts[0] == parts[1] else f"{parts[0]}~{parts[1]}")
            results.append({
                "title": item.get("title", ""),
                "place": item.get("placeName", ""),
                "region": item.get("regionName", ""),
                "date": date_str,
                "prod_id": str(item.get("prodId", "")),
            })
    except Exception as e:
        print(f"  멜론 수집 오류: {e}")
    return results


def is_large_venue(fclt_name):
    for kw in LARGE_VENUE_KEYWORDS:
        if kw.upper() in fclt_name.upper():
            return True
    return False


def match_artist(prfnm):
    if "내한" in prfnm:
        return None
    prfnm_upper = prfnm.upper()
    for kw in EXCLUDE_KEYWORDS:
        if kw.upper() in prfnm_upper:
            return None
    for artist, kws in ARTISTS.items():
        for kw in kws:
            if re.search(r'[A-Za-z]', kw):
                pat = r'(?<![A-Za-z])' + re.escape(kw) + r'(?![A-Za-z])'
                flags = 0 if kw in CASE_SENSITIVE else re.IGNORECASE
                if re.search(pat, prfnm, flags):
                    return artist
            else:
                if kw in prfnm:
                    return artist
    return None


def fmt_date(frm, to):
    frm = frm.replace(".", "-")
    to = to.replace(".", "-")
    return frm if frm == to else f"{frm}~{to}"


def is_duplicate(c, kopis_set):
    """멜론 공연이 KOPIS에 이미 있는지 확인 (아티스트 + 날짜 시작일 일치)"""
    start = c["날짜"].split("~")[0]
    key = (c["아티스트명"], start)
    return key in kopis_set


def main():
    print("KOPIS 수집 중...")
    all_perf = collect_all()
    concerts = []
    per_artist = {}
    excluded_small = []
    kopis_set = set()  # (아티스트명, 시작날짜) 중복 체크용

    for p in all_perf:
        artist = match_artist(p["prfnm"])
        if not artist:
            continue
        if artist not in SMALL_VENUE_OK:
            if not is_large_venue(p["fclt"]):
                excluded_small.append(f"{artist} | {p['prfnm']} | {p['fclt']}")
                continue
        date_str = fmt_date(p["from"], p["to"])
        concerts.append({
            "공연명": p["prfnm"],
            "아티스트명": artist,
            "지역또는장소": (p["fclt"] + " " + p["area"]).strip(),
            "날짜": date_str,
            "공연ID": p["id"],
            "출처": "KOPIS",
        })
        per_artist[artist] = per_artist.get(artist, 0) + 1
        kopis_set.add((artist, date_str.split("~")[0]))

    print("멜론티켓 수집 중...")
    melon_items = collect_melon()
    melon_added = []
    melon_excluded = []

    for m in melon_items:
        artist = match_artist(m["title"])
        if not artist:
            continue
        if artist not in SMALL_VENUE_OK:
            if not is_large_venue(m["place"]):
                melon_excluded.append(f"{artist} | {m['title']} | {m['place']}")
                continue
        c = {
            "공연명": m["title"],
            "아티스트명": artist,
            "지역또는장소": (m["place"] + " " + m["region"]).strip(),
            "날짜": m["date"],
            "공연ID": f"MELON_{m['prod_id']}",
            "출처": "멜론",
        }
        if is_duplicate(c, kopis_set):
            continue  # KOPIS에 이미 있으면 스킵
        concerts.append(c)
        melon_added.append(f"{artist} | {m['title']}")
        per_artist[artist] = per_artist.get(artist, 0) + 1

    with open("concerts.json", "w", encoding="utf-8") as f:
        json.dump(concerts, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 45)
    print("[KOPIS+멜론 수집 검증 요약]")
    print(f"대중음악 전체(KOPIS) : {len(all_perf)}건")
    print(f"K-Pop 매칭(KOPIS)   : {len([c for c in concerts if c['출처']=='KOPIS'])}건")
    print(f"멜론 추가(KOPIS 미등록): {len(melon_added)}건")
    for m in melon_added:
        print(f"  + {m}")
    print(f"멜론 공연장 미달 제외 : {len(melon_excluded)}건")
    print(f"최종 K-Pop 공연 합계 : {len(concerts)}건")
    print(f"매칭 아티스트 : {len(per_artist)}팀")
    print(f"아티스트별   : {per_artist}")
    print(f"KOPIS 공연장 미달 제외 : {len(excluded_small)}건")
    for ex in excluded_small:
        print(f"  제외: {ex}")
    print("샘플(최대10):")
    for c in concerts[:10]:
        print(f"  - {c['아티스트명']} | {c['공연명']} | {c['날짜']} | {c['지역또는장소']} [{c['출처']}]")
    print("-" * 45)
    print("[누락 진단] KOPIS 전체 공연명에 실제로 있는지:")
    for kw in DEBUG_CHECK:
        hits = [p["prfnm"] for p in all_perf if kw.lower() in p["prfnm"].lower()]
        sample = hits[0] if hits else "(없음)"
        print(f"  '{kw}': {len(hits)}건  예: {sample}")
    print("저장 파일    : concerts.json")
    print("=" * 45)


if __name__ == "__main__":
    main()
