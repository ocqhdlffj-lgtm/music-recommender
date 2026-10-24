import json, pathlib, sys, tempfile, unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import build


def write(text):
    f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    f.write(text); f.close()
    return f.name


class LoadSongs(unittest.TestCase):
    def test_real_data_is_valid(self):
        songs = build.load_songs()
        self.assertGreaterEqual(len(songs), 100)
        # 모든 기분·상황이 최소 5곡씩은 있어야 필터가 쓸모 있음
        for m in build.MOODS:
            self.assertGreaterEqual(sum(m in s[4] for s in songs), 5, m)
        for c in build.SCENES:
            self.assertGreaterEqual(sum(c in s[5] for s in songs), 5, c)

    def test_parses_line(self):
        p = write("# 주석\n\n제목|가수|2020|팝|신남,설렘|운동|소개\n")
        self.assertEqual(build.load_songs(p), [["제목", "가수", 2020, "팝", ["신남", "설렘"], ["운동"], "소개"]])

    def test_rejects_bad_rows(self):
        bad = {
            "칸이": "제목|가수|2020|팝|신남|운동\n",
            "장르": "제목|가수|2020|트로트|신남|운동|소개\n",
            "기분": "제목|가수|2020|팝|행복|운동|소개\n",
            "상황": "제목|가수|2020|팝|신남|산책|소개\n",
            "연도": "제목|가수|이천|팝|신남|운동|소개\n",
            "중복": "제목|가수|2020|팝|신남|운동|소개\n제목|가수|2021|팝|잔잔|운동|소개\n",
        }
        for word, text in bad.items():
            with self.subTest(word), self.assertRaisesRegex(AssertionError, word):
                build.load_songs(write(text))


class Render(unittest.TestCase):
    def test_injects_data_and_escapes_script_close(self):
        out = build.render([["</script>", "a", 2000, "팝", ["신남"], ["운동"], "n"]],
                           "<script>const SONGS = /*__SONGS__*/[];</script>")
        self.assertNotIn("/*__SONGS__*/", out)
        self.assertEqual(out.count("</script>"), 1)
        payload = out.split("SONGS = ")[1].split(";</script>")[0]
        self.assertEqual(json.loads(payload)[0][0], "</script>")

    def test_template_has_one_placeholder(self):
        self.assertIn("const SONGS =", build.render(build.load_songs()))


if __name__ == "__main__":
    unittest.main()
