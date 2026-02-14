#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class EncodeOptions:
    fmt: str
    quality: int
    optimize: bool


SUPPORTED_FORMATS = {"jpeg", "jpg", "png", "webp"}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Local CUI image compressor without Node.js (requires Pillow)."
    )
    parser.add_argument("input", type=Path, help="Input image path.")
    parser.add_argument("output", type=Path, help="Output image path.")
    parser.add_argument(
        "--format",
        "-f",
        dest="fmt",
        default="jpeg",
        help="Output format: jpeg, png, webp (default: jpeg).",
    )
    parser.add_argument(
        "--quality",
        "-q",
        type=int,
        default=75,
        help="Quality 1-100 for jpeg/webp (default: 75).",
    )
    parser.add_argument(
        "--optimize",
        action="store_true",
        help="Enable optimization for PNG output.",
    )
    return parser.parse_args()


def _load_pillow():
    if importlib.util.find_spec("PIL") is None:
        raise RuntimeError(
            "Pillow is required. Install it with: python -m pip install Pillow"
        )
    from PIL import Image  # type: ignore

    return Image


def _validate_options(options: EncodeOptions) -> EncodeOptions:
    fmt = options.fmt.lower()
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format '{options.fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )
    if not 1 <= options.quality <= 100:
        raise ValueError("Quality must be between 1 and 100.")
    return EncodeOptions(fmt=fmt, quality=options.quality, optimize=options.optimize)


def _compress_image(image_path: Path, output_path: Path, options: EncodeOptions) -> None:
    Image = _load_pillow()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(image_path) as img:
        save_kwargs: dict[str, object] = {}
        if options.fmt in {"jpeg", "jpg", "webp"}:
            save_kwargs["quality"] = options.quality
            save_kwargs["optimize"] = True
        if options.fmt == "png":
            save_kwargs["optimize"] = options.optimize
        img.save(output_path, format=options.fmt.upper(), **save_kwargs)


def main() -> int:
    args = _parse_args()
    options = _validate_options(
        EncodeOptions(fmt=args.fmt, quality=args.quality, optimize=args.optimize)
    )
    if not args.input.exists():
        raise FileNotFoundError(f"Input file not found: {args.input}")
    _compress_image(args.input, args.output, options)
    before_size = args.input.stat().st_size
    after_size = args.output.stat().st_size
    print(
        f"Saved: {args.output} ({before_size} bytes -> {after_size} bytes, format={options.fmt})"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
