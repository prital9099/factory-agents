"""Render a narrated MP4 from a scene-based HTML page.

Usage: python render_video.py <page.html> <out.mp4> [fps]

Page contract: #stage and #cap elements; .scene elements with data-start, data-end
(seconds) and data-say (narration); window.__seek(t) shows time t, window.__pause() stops
any internal clock. Needs: playwright (Chrome installed), imageio-ffmpeg, Windows (SAPI voice).
"""
import json, pathlib, subprocess, sys, tempfile

from playwright.sync_api import sync_playwright
import imageio_ffmpeg

html_path = pathlib.Path(sys.argv[1]).resolve()
out = pathlib.Path(sys.argv[2]).resolve()
fps = int(sys.argv[3]) if len(sys.argv) > 3 else 12
ff = imageio_ffmpeg.get_ffmpeg_exe()
work = pathlib.Path(tempfile.mkdtemp(prefix="render_video_"))

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1280, "height": 900})
    pg.goto(html_path.as_uri())
    pg.wait_for_timeout(1500)
    pg.evaluate("document.fonts.ready")
    scenes = pg.evaluate("[...document.querySelectorAll('.scene')].map(s=>({start:+s.dataset.start,end:+s.dataset.end,say:s.dataset.say||''}))")
    total = max(s["end"] for s in scenes)
    pg.evaluate("window.__pause()")
    box = pg.evaluate("(()=>{const a=document.getElementById('stage').getBoundingClientRect(),c=document.getElementById('cap').getBoundingClientRect();return {y:a.top,h:c.bottom-a.top}})()")
    clip = {"x": 0, "y": box["y"], "width": 1280, "height": int(box["h"]) // 2 * 2}

    # narration: one Windows SAPI clip per scene
    (work / "scenes.json").write_text(json.dumps(scenes), encoding="utf-8")
    ps = ('Add-Type -AssemblyName System.Speech;'
          '$j=Get-Content "%s\scenes.json" -Raw -Encoding UTF8|ConvertFrom-Json;'
          '$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;$s.Rate=1;'
          'try{$s.SelectVoice("Microsoft Zira Desktop")}catch{};$i=0;'
          'foreach($x in $j){$s.SetOutputToWaveFile("%s\s$i.wav");$s.Speak($x.say);$s.SetOutputToNull();$i++};$s.Dispose()') % (work, work)
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)

    silent = work / "silent.mp4"
    enc = subprocess.Popen([ff, "-y", "-f", "image2pipe", "-framerate", str(fps), "-i", "-", "-c:v", "libx264",
                            "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart", str(silent)],
                           stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    starts = [s["start"] for s in scenes]
    for i in range(int(total * fps)):
        t = i / fps
        pg.evaluate("t=>window.__seek(t)", t)
        ss = max(x for x in starts if x <= t)
        pg.evaluate("ms=>document.getAnimations().forEach(a=>{a.pause();a.currentTime=ms})", (t - ss) * 1000)
        enc.stdin.write(pg.screenshot(clip=clip, type="jpeg", quality=92))
    enc.stdin.close(); enc.wait(); b.close()

args = [ff, "-y", "-i", str(silent)]
for i in range(len(scenes)): args += ["-i", str(work / f"s{i}.wav")]
fc = ";".join(f"[{i+1}:a]adelay={int(s['start']*1000)+100}|{int(s['start']*1000)+100}[a{i}]" for i, s in enumerate(scenes))
fc += ";" + "".join(f"[a{i}]" for i in range(len(scenes))) + f"amix=inputs={len(scenes)}:normalize=0,apad=whole_dur={total}[a]"
args += ["-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
         "-t", str(total), "-movflags", "+faststart", str(out)]
subprocess.run(args, check=True, capture_output=True)
print("wrote", out, f"{total}s")
