# -*- coding: utf-8 -*-
"""ダンプ法令ラジオ ― 台本(radio.json) から音声のみのMP3を作る。

声は open-jtalk（オフラインの日本語音声合成）1種類しかないので、
話し手ごとに高さ(-fm)・声道(-a)・速さ(-r)を変えて2人に聞こえるようにしている。
外部のサービスには何も送っていない。

出力:
  ダンプ法令ラジオ.mp3   本体
  台本.md                 章立て・時刻つきの読み原稿（radio.json から作る）

使い方:  python3 src/gen.py
"""
import io
import json
import pathlib
import re
import subprocess
import wave

D = pathlib.Path(__file__).parent
OUT = D / "build"
OUT.mkdir(exist_ok=True)
DIC = "/var/lib/mecab/dic/open-jtalk/naist-jdic"
VOICE = "/usr/share/hts-voice/nitech-jp-atr503-m001/nitech_jp_atr503_m001.htsvoice"

# 話し手ごとの声。fm=高さ(半音)、a=声道の太さ、r=速さ
# 実測で およそ182Hz と 136Hz。5半音ほど離れているので別人に聞こえる。
TONE = {"A": {"fm": "4.0", "a": "0.48", "r": "1.08"},
        "B": {"fm": "-1.0", "a": "0.57", "r": "1.00"}}

# 音声合成が読み間違える語。台本の表記は変えず、読ませる文字列だけ差し替える。
YOMI = [
    ("傭車", "ようしゃ"), ("自重計", "じじゅうけい"), ("車検証", "しゃけんしょう"),
    ("土砂等", "どしゃとう"), ("積込み", "積み込み"), ("積込", "積み込み"),
    ("白ダンプ", "しろダンプ"), ("緑ダンプ", "みどりダンプ"),
    ("荷台", "にだい"), ("元請", "もとうけ"), ("下請", "したうけ"),
    ("日雇い", "ひやとい"), ("砕石", "さいせき"), ("砂利", "じゃり"),
    ("残土", "ざんど"), ("汚泥", "おでい"), ("選任", "せんにん"),
    ("点呼", "てんこ"), ("領置", "りょうち"), ("附則", "ふそく"),
    ("場内", "じょうない"), ("公道", "こうどう"), ("横持ち", "よこもち"),
    ("着地渡し", "ちゃくちわたし"), ("一人親方", "ひとりおやかた"),
]

GAP_LINE = 0.28      # セリフとセリフの間
GAP_SPEAKER = 0.42   # 話し手が替わるとき
GAP_CHAPTER = 1.1    # 章のあいだ


def say(text, sp, path):
    t = text
    for a, b in YOMI:
        t = t.replace(a, b)
    src = OUT / "tmp.txt"
    io.open(src, "w", encoding="utf-8").write(t)
    o = TONE[sp]
    subprocess.run(["open_jtalk", "-x", DIC, "-m", VOICE,
                    "-fm", o["fm"], "-a", o["a"], "-r", o["r"],
                    "-ow", str(path), str(src)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with wave.open(str(path)) as w:
        return w.getnframes() / float(w.getframerate()), w.getframerate()


def silence(sec, path, rate):
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi",
                    "-i", "anullsrc=r=%d:cl=mono" % rate, "-t", "%.3f" % sec,
                    "-c:a", "pcm_s16le", str(path)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def chime(path, rate):
    """章の区切りの合図。2音の短いトーン。"""
    f = ("sine=frequency=880:duration=0.16,volume=0.16,afade=t=out:st=0.10:d=0.06[a];"
         "sine=frequency=1320:duration=0.20,volume=0.13,afade=t=out:st=0.10:d=0.10[b];"
         "[a][b]concat=n=2:v=0:a=1")
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=%d:cl=mono" % rate,
                    "-filter_complex", f, "-map", "[out]" if False else "0:a",
                    "-t", "0.01", "-c:a", "pcm_s16le", str(OUT / "_x.wav")],
                   check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # 上の書き方は環境差が出るので、2音を別々に作ってつなぐ
    parts = []
    for i, (hz, vol) in enumerate([(880, 0.16), (1320, 0.13)]):
        p = OUT / ("chime%d.wav" % i)
        subprocess.run(["ffmpeg", "-y", "-f", "lavfi",
                        "-i", "sine=frequency=%d:duration=0.18:sample_rate=%d" % (hz, rate),
                        "-af", "volume=%.2f,afade=t=out:st=0.09:d=0.09" % vol,
                        "-ac", "1", "-c:a", "pcm_s16le", str(p)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        parts.append(p)
    lst = OUT / "chime.txt"
    io.open(lst, "w", encoding="utf-8").write("".join("file '%s'\n" % p.name for p in parts))
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c", "copy", str(path)],
                   check=True, cwd=str(OUT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with wave.open(str(path)) as w:
        return w.getnframes() / float(w.getframerate())


def main():
    data = json.loads((D / "radio.json").read_text(encoding="utf-8"))
    names = data["speakers"]
    pieces, marks, t = [], [], 0.0
    rate = None
    prev_sp = None
    n = 0

    for item in data["script"]:
        if item["type"] == "chapter":
            if rate:
                g = OUT / ("gap_c%d.wav" % item["no"])
                silence(GAP_CHAPTER / 2, g, rate)
                pieces.append(g); t += GAP_CHAPTER / 2
                ch = OUT / "chime.wav"
                t += chime(ch, rate)
                pieces.append(ch)
                g2 = OUT / ("gap_c%db.wav" % item["no"])
                silence(GAP_CHAPTER / 2, g2, rate)
                pieces.append(g2); t += GAP_CHAPTER / 2
            marks.append((t, item["no"], item["title"]))
            prev_sp = None
            continue

        w = OUT / ("l%04d.wav" % n)
        dur, r = say(item["text"], item["sp"], w)
        rate = rate or r
        if pieces:
            gap = GAP_SPEAKER if item["sp"] != prev_sp else GAP_LINE
            g = OUT / ("g%04d.wav" % n)
            silence(gap, g, rate)
            pieces.append(g); t += gap
        item["_at"] = t
        pieces.append(w); t += dur
        prev_sp = item["sp"]
        n += 1
        if n % 40 == 0:
            print("  %d行 / %s" % (n, fmt(t)))

    lst = OUT / "all.txt"
    io.open(lst, "w", encoding="utf-8").write("".join("file '%s'\n" % p.name for p in pieces))
    mp3 = D.parent / "ダンプ法令ラジオ.mp3"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-af", "loudnorm=I=-18:TP=-2:LRA=11",
                    "-c:a", "libmp3lame", "-b:a", "64k", "-ar", "44100", "-ac", "1",
                    "-metadata", "title=%s" % data["title"],
                    "-metadata", "artist=有限会社石名坂商事・株式会社石名坂",
                    str(mp3)],
                   check=True, cwd=str(OUT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    write_script(data, marks, t)
    print("wrote %s  （%s）" % (mp3.name, fmt(t)))


def fmt(s):
    return "%d:%02d" % (int(s) // 60, int(s) % 60)


def write_script(data, marks, total):
    L = ["# %s" % data["title"], "",
         "音声のみの社内向け番組です。**全%s。**運転席でも配車室でも、聞くだけで分かるように作ってあります。" % fmt(total),
         "表も図も出てきません。",
         "", "- 音声：[`ダンプ法令ラジオ.mp3`](ダンプ法令ラジオ.mp3)",
         "- この台本は `src/radio.json` から作っています。**直すときは radio.json を直してください。**", "",
         "## 章立て", "", "| 時刻 | 章 |", "|---|---|"]
    for at, no, title in marks:
        L.append("| %s | %d　%s |" % (fmt(at), no, title))
    L += ["", "声は2人とも open-jtalk（オフラインの音声合成）で、高さと速さを変えて作り分けています。",
          "外部のサービスには何も送っていません。機械的な声なので、正式版はご自身の声で",
          "録り直していただくほうが聞きやすいはずです。その場合はこの台本をそのまま読んでください。", "",
          "---", ""]
    names = data["speakers"]
    for item in data["script"]:
        if item["type"] == "chapter":
            L += ["", "## %d　%s" % (item["no"], item["title"]), ""]
        else:
            L.append("**%s**　%s" % (names[item["sp"]], item["text"]))
            L.append("")
    io.open(D.parent / "台本.md", "w", encoding="utf-8").write("\n".join(L))


if __name__ == "__main__":
    main()
