# -*- coding: utf-8 -*-
"""スライドHTML → PNG、ナレーション → WAV、まとめてMP4。"""
import io, os, re, sys, json, subprocess, pathlib, wave

D = pathlib.Path(__file__).parent
OUT = D / 'build'
OUT.mkdir(exist_ok=True)
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
DIC = "/var/lib/mecab/dic/open-jtalk/naist-jdic"
VOICE = "/usr/share/hts-voice/nitech-jp-atr503-m001/nitech_jp_atr503_m001.htsvoice"

# 読み間違いの置換（音声用のみ。台本の表記は変えない）
YOMI = [('傭車', 'ようしゃ'), ('自重計', 'じじゅう計'), ('車検証', 'しゃけん証'),
        ('引取販売', '引取り販売'), ('積込み', '積み込み'), ('積込', '積み込み')]

def say(text, path):
    t = text
    for a, b in YOMI:
        t = t.replace(a, b)
    src = OUT / 'tmp.txt'
    io.open(src, 'w', encoding='utf-8').write(t)
    subprocess.run(['open_jtalk', '-x', DIC, '-m', VOICE, '-r', '1.05',
                    '-ow', str(path), str(src)], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with wave.open(str(path)) as w:
        return w.getnframes() / float(w.getframerate())

def page_html(inner):
    return ('<!doctype html><html lang="ja"><head><meta charset="utf-8">'
            '<link rel="stylesheet" href="style.css"></head><body>%s</body></html>' % inner)

def render(slides):
    import shutil
    shutil.copy(str(D / 'style.css'), str(OUT / 'style.css'))
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        pg = b.new_page(viewport={'width': 1920, 'height': 1080},
                        device_scale_factor=1)
        for i, s in enumerate(slides):
            f = OUT / ('s%03d.html' % i)
            io.open(f, 'w', encoding='utf-8').write(page_html(s['html']))
            pg.goto(f.as_uri(), wait_until='networkidle')
            over = pg.evaluate("() => {const e=document.querySelector('.slide');"
                               "return [e.scrollHeight, e.scrollWidth];}")
            if over[0] > 1082 or over[1] > 1922:
                print('  ! OVERFLOW slide %d: %sx%s' % (i, over[1], over[0]))
            pg.screenshot(path=str(OUT / ('s%03d.png' % i)))
        b.close()

def srt_time(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return '%02d:%02d:%06.3f' % (h, m, s).replace('.', ',') if False else \
           '%02d:%02d:%02d,%03d' % (h, m, int(s), round((s - int(s)) * 1000))

def main(slides, name='解説動画'):
    render(slides)
    durs, srt, t0 = [], [], 0.0
    for i, s in enumerate(slides):
        wav = OUT / ('a%03d.wav' % i)
        nar = s.get('narration', '').strip()
        if nar:
            d = say(nar, wav)
        else:
            d = float(s.get('hold', 2.0))
            subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i',
                            'anullsrc=r=48000:cl=mono', '-t', str(d), str(wav)],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pre, post = s.get('pre', 0.35), s.get('post', 0.7)
        total = pre + d + post
        durs.append((i, pre, d, post, total))
        if nar:
            # 1文ずつに割って、文字数の比で時間を配る
            sents = [x for x in re.split(r'(?<=。)', nar) if x.strip()]
            chunks, cur = [], ''
            for x in sents:
                if len(cur) + len(x) <= 38 or not cur:
                    cur += x
                else:
                    chunks.append(cur); cur = x
            if cur: chunks.append(cur)
            total_c = sum(len(c) for c in chunks) or 1
            tc = t0 + pre
            for c in chunks:
                dd = d * len(c) / total_c
                srt.append((len(srt) + 1, tc, tc + dd, c))
                tc += dd
        t0 += total
    # 音声：前後の無音を足して連結
    with io.open(OUT / 'alist.txt', 'w', encoding='utf-8') as f:
        for i, pre, d, post, total in durs:
            sil_a = OUT / ('p%03d.wav' % i); sil_b = OUT / ('q%03d.wav' % i)
            for path, sec in ((sil_a, pre), (sil_b, post)):
                subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i',
                                'anullsrc=r=48000:cl=mono', '-t', str(sec), str(path)],
                               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            for path in (sil_a, OUT / ('a%03d.wav' % i), sil_b):
                f.write("file '%s'\n" % path.name)
    subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', 'alist.txt',
                    '-ar', '48000', '-ac', '1', 'voice.wav'], cwd=str(OUT), check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # 映像：静止画をつなぐ
    with io.open(OUT / 'vlist.txt', 'w', encoding='utf-8') as f:
        for i, pre, d, post, total in durs:
            f.write("file 's%03d.png'\nduration %.3f\n" % (i, total))
        f.write("file 's%03d.png'\n" % durs[-1][0])
    subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', 'vlist.txt',
                    '-i', 'voice.wav', '-vf', 'fps=25,format=yuv420p',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-tune', 'stillimage', '-crf', '24',
                    '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart',
                    '%s.mp4' % name], cwd=str(OUT), check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', 'vlist.txt',
                    '-vf', 'fps=25,format=yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-tune', 'stillimage',
                    '-crf', '24', '-movflags', '+faststart', '%s（無音）.mp4' % name],
                   cwd=str(OUT), check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with io.open(OUT / ('%s.srt' % name), 'w', encoding='utf-8') as f:
        for n, a, b, txt in srt:
            f.write('%d\n%s --> %s\n%s\n\n' % (n, srt_time(a), srt_time(b),
                                               re.sub(r'\s+', '', txt)))
    print('slides=%d  total=%.1fs (%d分%02d秒)' % (len(slides), t0, int(t0 // 60), int(t0 % 60)))
    return t0
