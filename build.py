#!/usr/bin/env python3
"""data/songs.txt + data/chart_songs.txt + src/template.html -> music-recommender.html (단일 파일, 외부 의존성 없음).

사용법:  python build.py          (HTML 생성)
         python build.py --check  (형식 검증만, 파일은 안 씀)
"""
import json, sys, pathlib

ROOT = pathlib.Path(__file__).parent
MOODS = ["신남","잔잔","위로","설렘","그리움"]
SCENES = ["운동","드라이브","출근길","공부·작업","비 오는 날","잠들기 전"]
GENRES = ["발라드","K-pop","포크","인디/밴드","록","팝","R&B/소울","댄스/일렉트로닉","힙합","컨트리","트로트","재즈","J-pop","클래식/뉴에이지"]
# 앞 파일이 우선: 직접 고른 곡과 겹치는 차트 곡은 건너뜀
FILES = [ROOT/"data/songs.txt", ROOT/"data/chart_songs.txt"]
PLACEHOLDER = "/*__SONGS__*/[]"

def load_songs(path=ROOT/"data/songs.txt"):
    songs, seen = [], set()
    name = pathlib.Path(path).name
    for n, line in enumerate(pathlib.Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.startswith("#"): continue
        f = line.split("|")
        assert len(f) == 7, f"{name} {n}행: 칸이 {len(f)}개 (7개여야 함): {line[:40]}"
        t, a, y, g, m, s, note = (x.strip() for x in f)
        assert t and a and note, f"{name} {n}행: 제목·가수·소개는 비울 수 없음"
        assert y.isdigit() and 1600 <= int(y) <= 2100, f"{name} {n}행: 연도 '{y}' 오류"
        assert g in GENRES, f"{name} {n}행: 장르 '{g}' 미등록"
        moods, scenes = m.split(","), s.split(",")
        for x in moods: assert x in MOODS, f"{name} {n}행: 기분 '{x}' 미등록"
        for x in scenes: assert x in SCENES, f"{name} {n}행: 상황 '{x}' 미등록"
        key = (t.lower(), a.lower())
        assert key not in seen, f"{name} {n}행: 중복 {t} / {a}"
        seen.add(key)
        songs.append([t, a, int(y), g, moods, scenes, note])
    return songs

def load_all(files=FILES):
    songs, seen = [], set()
    for f in files:
        for s in load_songs(f):
            key = (s[0].lower(), s[1].lower())
            if key in seen: continue
            seen.add(key); songs.append(s)
    return songs

def render(songs, template=None):
    template = template or (ROOT/"src/template.html").read_text(encoding="utf-8")
    assert template.count(PLACEHOLDER) == 1, "template.html: 데이터 자리표시자가 정확히 1개여야 함"
    # </script> 조기 종료 방지
    data = json.dumps(songs, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return template.replace(PLACEHOLDER, data)

def main(argv):
    songs = load_all()
    print(f"{len(songs)}곡 검증 통과")
    if "--check" in argv: return
    (ROOT/"music-recommender.html").write_text(render(songs), encoding="utf-8")
    print("music-recommender.html 생성")

if __name__ == "__main__":
    main(sys.argv[1:])
