#!/usr/bin/env python3
"""
MP4 Screen Recording to Word Document Converter

This script extracts frames from an .mp4 video file at a configurable interval
and generates a Word document containing each frame as an image. Optionally,
it uses OCR (Tesseract) to extract text content from each frame.

Usage:
    python mp4_to_word.py input.mp4 -o output.docx
    python mp4_to_word.py input.mp4 --interval 2 --ocr
"""

import argparse
import os
import sys
import tempfile

import cv2
from docx import Document
from docx.shared import Inches
from PIL import Image


def extract_frames(video_path, interval_seconds=1.0):
    """Extract frames from a video file at the specified interval.

    Args:
        video_path: Path to the .mp4 video file.
        interval_seconds: Time interval in seconds between extracted frames.

    Yields:
        Tuples of (frame_index, timestamp_seconds, frame_bgr_array).
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video file: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        raise ValueError(f"Invalid FPS ({fps}) in video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_interval = max(1, int(fps * interval_seconds))

    frame_index = 0
    extracted = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_index % frame_interval == 0:
            timestamp = frame_index / fps
            yield extracted, timestamp, frame
            extracted += 1

        frame_index += 1

    cap.release()


def ocr_frame(frame_bgr, lang="eng+chi_sim"):
    """Run OCR on a video frame to extract text.

    Args:
        frame_bgr: Frame as a BGR numpy array (from OpenCV).
        lang: Tesseract language string. Default includes English and
              Simplified Chinese.

    Returns:
        Extracted text as a string, or an error message if OCR fails.
    """
    try:
        import pytesseract
    except ImportError:
        return "[pytesseract is not installed — skipping OCR]"

    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb)

    try:
        text = pytesseract.image_to_string(pil_image, lang=lang)
    except Exception as exc:
        return f"[OCR error: {exc}]"

    return text.strip()


def build_word_document(video_path, output_path, interval_seconds=1.0,
                        enable_ocr=False, image_width_inches=6.0):
    """Build a Word document from video frames.

    Args:
        video_path: Path to the .mp4 video file.
        output_path: Path for the output .docx file.
        interval_seconds: Seconds between extracted frames.
        enable_ocr: Whether to run OCR on each frame.
        image_width_inches: Width of each frame image in the document.
    """
    doc = Document()
    doc.add_heading("Screen Recording — Frame Export", level=1)

    video_name = os.path.basename(video_path)
    doc.add_paragraph(f"Source: {video_name}")
    doc.add_paragraph(f"Frame interval: {interval_seconds}s")
    doc.add_paragraph("")

    with tempfile.TemporaryDirectory() as tmp_dir:
        for idx, timestamp, frame in extract_frames(video_path,
                                                    interval_seconds):
            minutes = int(timestamp // 60)
            seconds = timestamp % 60
            time_label = f"{minutes:02d}:{seconds:05.2f}"

            doc.add_heading(f"Frame {idx + 1}  ({time_label})", level=2)

            img_path = os.path.join(tmp_dir, f"frame_{idx:05d}.png")
            cv2.imwrite(img_path, frame)

            doc.add_picture(img_path, width=Inches(image_width_inches))

            if enable_ocr:
                text = ocr_frame(frame)
                if text:
                    doc.add_heading("OCR Text", level=3)
                    doc.add_paragraph(text)

            doc.add_page_break()

            if (idx + 1) % 10 == 0:
                print(f"  Processed {idx + 1} frames …")

    doc.save(output_path)
    print(f"Saved Word document to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert an MP4 screen recording to a Word document, "
                    "frame by frame."
    )
    parser.add_argument("input", help="Path to the .mp4 video file")
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output .docx file path (default: <input_name>.docx)"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Seconds between extracted frames (default: 1.0)"
    )
    parser.add_argument(
        "--ocr",
        action="store_true",
        help="Enable OCR text extraction for each frame "
             "(requires Tesseract installed)"
    )
    parser.add_argument(
        "--width",
        type=float,
        default=6.0,
        help="Image width in inches inside the Word document (default: 6.0)"
    )

    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    output = args.output
    if output is None:
        base = os.path.splitext(os.path.basename(args.input))[0]
        output = base + ".docx"

    build_word_document(
        video_path=args.input,
        output_path=output,
        interval_seconds=args.interval,
        enable_ocr=args.ocr,
        image_width_inches=args.width,
    )


if __name__ == "__main__":
    main()
