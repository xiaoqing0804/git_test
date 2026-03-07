# MP4 Screen Recording to Word Converter

将 `.mp4` 录屏文件逐帧提取并生成 Word（`.docx`）文档。  
支持按时间间隔抽帧，可选 OCR 文字识别。

## 方案概述

1. **视频抽帧** — 使用 OpenCV 按指定时间间隔从 `.mp4` 文件中提取帧。
2. **图片写入 Word** — 使用 python-docx 将每帧图片插入到 Word 文档，并标注时间戳。
3. **AI 文字识别（可选）** — 使用 Tesseract OCR（通过 pytesseract）对每帧进行文字识别，将提取到的文本附在图片下方。

## 环境准备

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# （可选）安装 Tesseract OCR 引擎，用于文字识别
# macOS
brew install tesseract tesseract-lang
# Ubuntu / Debian
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim
```

## 使用方法

```bash
# 基本用法 — 每秒取 1 帧
python mp4_to_word.py recording.mp4 -o output.docx

# 每 2 秒取 1 帧
python mp4_to_word.py recording.mp4 --interval 2

# 启用 OCR 文字提取
python mp4_to_word.py recording.mp4 --ocr

# 自定义图片宽度（英寸）
python mp4_to_word.py recording.mp4 --width 5.5
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `input` | 输入的 `.mp4` 视频文件路径 | （必填） |
| `-o / --output` | 输出的 `.docx` 文件路径 | `<输入文件名>.docx` |
| `--interval` | 抽帧间隔（秒） | `1.0` |
| `--ocr` | 启用 OCR 文字识别 | 关闭 |
| `--width` | Word 中图片宽度（英寸） | `6.0` |

## 项目结构

```
mp4_to_word.py      # 主程序
requirements.txt    # Python 依赖
README.md           # 说明文档
```