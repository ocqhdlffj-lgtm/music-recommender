#!/usr/bin/env python3
"""data/songs.txt + src/template.html -> music-recommender.html (단일 파일, 외부 의존성 없음).

사용법:  python build.py          (HTML 생성)
         python build.py --check  (형식 검증만, 파일은 안 씀)
"""
import json, sys, pathlib

ROOT = pathlib.Path(__file__).parent
MOODS = ["신남","잔잔","위로","설렘","그리움"]
SCENES = ["운동","드라이브","출근길","공부·작업","비 오는 날","잠들기 전"]
GENRES = ["발라드","K-pop","포크","인디/밴드","록","팝","재즈","힙합","J-pop","클래식/뉴에이지"]
PLACEHOLDER = "/*__SONGS__*/[]"

def load_songs(path=ROOT/"data/songs.txt"):
    songs, seen = [], set()
    for n, line in enumerate(pathlib.Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.startswith("#"): continue
        f = line.split("|")
        assert len(f) == 7, f"songs.txt {n}행: 칸이 {len(f)}개 (7개여야 함): {line[:40]}"
        t, a, y, g, m, s, note = (x.strip() for x in f)
        assert t and a and note, f"songs.txt {n}행: 제목·가수·소개는 비울 수 없음"
        assert y.isdigit() and 1600 <= int(y) <= 2100, f"songs.txt {n}행: 연도 '{y}' 오류"
        assert g in GENRES, f"songs.txt {n}행: 장르 '{g}' 미등록"
        moods, scenes = m.split(","), s.split(",")
        for x in moods: assert x in MOODS, f"songs.txt {n}행: 기분 '{x}' 미등록"
        for x in scenes: assert x in SCENES, f"songs.txt {n}행: 상황 '{x}' 미등록"
        key = (t.lower(), a.lower())
        assert key not in seen, f"songs.txt {n}행: 중복 {t} / {a}"
        seen.add(key)
        songs.append([t, a, int(y), g, moods, scenes, note])
    return songs

def render(songs, template=None):
    template = template or (ROOT/"src/template.html").read_text(encoding="utf-8")
    assert template.count(PLACEHOLDER) == 1, "template.html: 데이터 자리표시자가 정확히 1개여야 함"
    # </script> 조기 종료 방지
    data = json.dumps(songs, ensure_ascii=False).replace("</", "<\\/")
    return template.replace(PLACEHOLDER, data)

def main(argv):
    songs = load_songs()
    print(f"{len(songs)}곡 검증 통과")
    if "--check" in argv: return
    (ROOT/"music-recommender.html").write_text(render(songs), encoding="utf-8")
    print("music-recommender.html 생성")

if __name__ == "__main__":
    main(sys.argv[1:])
