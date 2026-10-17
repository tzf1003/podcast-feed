#!/usr/bin/env python3
import subprocess, sys
sys.path.insert(0, '/home/hatch/workspace/custom-connectors/custom.dashscope/bin')
from qwen_tts_podcast import synthesize_turn
from pathlib import Path

JOE = "qwen-audio-3.1-tts-flash-bailian-fe563dbc564843bf9226fb68a35f8653"
CODY = "anmingyuan_v3.1"
BACKCHANNELS = {"对", "对啊", "嗯", "是", "好吧", "有道理", "没错", "可不", "那倒是", "对，好吧，"}

def get_duration(path):
    r = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration',
                        '-of','csv=p=0', str(path)], capture_output=True, text=True)
    return float(r.stdout.strip())

script = Path('/home/hatch/workspace/jre-test/jre-2566-full-zh.txt')
outdir = Path('/home/hatch/workspace/jre-test/turns-full')
outdir.mkdir(exist_ok=True)

lines = [l.strip() for l in script.read_text().splitlines() if l.strip()]
print(f"共 {len(lines)} 句", flush=True)

# 逐句合成（跳过已存在的）
for i, line in enumerate(lines):
    if ': ' not in line:
        continue
    speaker, text = line.split(': ', 1)
    voice = JOE if 'Joe' in speaker else CODY
    out = outdir / f"turn_{i:04d}.mp3"
    if not out.exists():
        try:
            synthesize_turn(text, voice, str(out))
        except Exception as e:
            print(f"FAIL {i}: {e}", flush=True)
            continue
    if i % 100 == 0:
        print(f"进度: {i}/{len(lines)}", flush=True)

print("合成完成，开始混音...", flush=True)
