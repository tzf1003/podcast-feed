# JRE #2566 中文版 · 交接文档

**日期**：2026-10-17
**节目**：The Joe Rogan Experience #2566 - Cody Tucker
**目标**：3 小时中文版，发布到 jre-zh 独立 feed

---

## 当前状态（交接时）

| 环节 | 状态 |
|------|------|
| 原音频下载 | ✅ 完成 `jre-2566-full.mp3`（143MB，2h58m） |
| Whisper 转录 | ✅ 完成 3510 段 `jre-2566-full-transcript.txt` |
| 中文翻译 | ✅ 完成 3476 句 `jre-2566-full-zh.txt`（自然口语，非直译） |
| TTS 合成 | ⏸️ **进行中 2567/3476（74%）**，在原 VM 上被手动停止 |
| 重叠混音 | ❌ 未开始 |
| Demucs 背景分离 | ❌ 未开始（10 分钟测试版已验证流程） |
| 音量归一化 | ❌ 未开始 |
| 发布到 jre-zh | ❌ 未开始 |

---

## 声音配置（已固定）

| 角色 | 声音 | voice_id |
|------|------|----------|
| Joe Rogan | 复刻音色 | `qwen-audio-3.1-tts-flash-bailian-fe563dbc564843bf9226fb68a35f8653` |
| 男嘉宾（固定） | 陈默 | `anmingyuan_v3.1` |
| 女嘉宾（固定） | 晓雯 | `xieshurou_v3.1` |

- 模型：`qwen-audio-3.1-tts-flash`
- 说话人分配规则：英文转录时长 >2s = Joe Rogan，≤2s = Cody Tucker（背板音/插话）
- API key 在 Secure Vault：`custom.dashscope`
- 合成脚本：`~/workspace/custom-connectors/custom.dashscope/bin/qwen_tts_podcast.py`（`synthesize_turn(text, voice, out_path)` 可单独调用）

---

## 已合成的 2567 个文件

位置（原 VM）：`~/workspace/jre-test/turns-full/turn_0000.mp3` ~ `turn_2566.mp3`（约 349MB）

**注意**：文件名编号对应 `jre-2566-full-zh.txt` 的行号（0-indexed）。例如 `turn_0000.mp3` 是第 1 行。

### 两种继续方式

**方式 A：复制已有文件 + 续跑剩余**
1. 从原 VM 复制 `turns-full/` 到新环境（SCP/rsync，约 349MB）
2. 在新环境运行 `synth_full.py`（见下），脚本幂等，自动跳过已存在文件，从 turn_2567 继续

**方式 B：从头重跑（推荐，如果网络快）**
- 3476 次 API 调用，在高配环境约 1-2 小时
- 直接运行 `synth_full.py` 即可

---

## 续跑合成脚本

`synth_full.py`（在 `jre-zh/work/` 下）：

```python
# 核心逻辑：
# 1. 读 jre-2566-full-zh.txt（3476 行，格式 "Joe Rogan: 中文" / "Cody Tucker: 中文"）
# 2. 每行调 synthesize_turn(text, voice, out_path)
#    - Joe Rogan → joerogan voice_id
#    - Cody Tucker → anmingyuan_v3.1
# 3. 输出到 turns-full/turn_{i:04d}.mp3
# 4. 已存在则跳过（幂等）
```

运行：`python3 synth_full.py`（后台：`nohup python3 synth_full.py >> synth_full.log 2>&1 &`）

---

## 合成完成后的步骤

### 1. 重叠混音

短插话（backchannel）要叠到上一句尾部，不是顺序播放。

Backchannel 判定：文本在 `{"对","对啊","嗯","是","好吧","有道理","没错","可不","那倒是"}` 或音频时长 <1.2s

混音逻辑：
- 正常句：顺序排列
- Backchannel：开始时间 = 上一句结束时间 - 0.4s（提前 0.4 秒叠上去）
- 用 ffmpeg `adelay` + `amix` 实现

参考脚本：`synth_overlap.py`（2 分钟测试版，需改写适配 3476 句）

### 2. Demucs 背景分离

```bash
python3 -m demucs --two-stems=vocals jre-2566-full.mp3
# 输出：vocals.wav（人声） + no_vocals.wav（背景：房间声、笑声、气口、BGM）
```

### 3. 最终混音

```
no_vocals.wav（原版背景） + 中文人声轨（重叠混音结果）
→ ffmpeg amix
→ loudnorm 音量归一化（用户明确要求：调高音量，与原版响度一致）
```

### 4. 发布到 jre-zh feed

```bash
python3 ~/workspace/podcasts/feed-gen/publish_episode.py \
  --show jre-zh \
  --mp3 <最终mp3路径> \
  --slug jre-2566-zh \
  --title "Joe Rogan 中文版 #2566 - Cody Tucker" \
  --description "The Joe Rogan Experience #2566 中文版" \
  --pub-date 2026-10-17T01:00:00+00:00 \
  --duration <时长秒数取整>
```

Feed：https://tzf1003.github.io/podcast-feed/jre-zh/feed.xml

---

## 文件清单（本目录）

| 文件 | 说明 |
|------|------|
| `HANDOFF.md` | 本文档 |
| `jre-2566-full-zh.txt` | 3476 句中文脚本（合成输入） |
| `jre-2566-full-transcript.txt` | 3510 段英文转录（含时间戳） |
| `synth_full.py` | 续跑合成脚本（幂等） |

---

## 已验证的经验

1. **音色**：Joe 用复刻音色，男嘉宾固定用陈默，女嘉宾固定用晓雯。用户已确认区分度 OK。
2. **翻译**：自然口语，不逐句直译。用户确认"翻译自然度够了"。
3. **重叠**：backchannel 提前 0.4s 叠加，用户确认"效果对了"。
4. **音量**：之前混音版音量偏低，最终版必须做 loudnorm 归一化。
5. **API**：`custom.dashscope` 凭证健康。注意：在某些沙箱/后台上下文中 egress 会被拦截 403，必须在正常主聊天/agent 上下文运行合成。
