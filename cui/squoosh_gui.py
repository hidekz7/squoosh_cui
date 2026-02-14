#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from cui.squoosh_cui import EncodeOptions, _compress_image, _validate_options

_DND_AVAILABLE = importlib.util.find_spec("tkinterdnd2") is not None
if _DND_AVAILABLE:
    from tkinterdnd2 import DND_FILES, TkinterDnD  # type: ignore


@dataclass
class PreviewImages:
    original: object | None = None
    compressed: object | None = None


class SquooshGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Squoosh CUI GUI")
        self.files: list[Path] = []
        self.preview_images = PreviewImages()

        self.output_dir = tk.StringVar(
            value=str(Path.cwd() / "resized"),
        )
        self.format_var = tk.StringVar(value="jpeg")
        self.quality_var = tk.IntVar(value=75)
        self.optimize_var = tk.BooleanVar(value=False)

        self._build_ui()

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=12)
        main.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        drop_frame = ttk.LabelFrame(main, text="Input files", padding=8)
        drop_frame.grid(row=0, column=0, sticky="ew")
        drop_frame.columnconfigure(0, weight=1)

        drop_label = ttk.Label(
            drop_frame,
            text="Drag and drop images here (or use Add Files)",
            anchor="center",
        )
        drop_label.grid(row=0, column=0, sticky="ew", pady=4)

        if _DND_AVAILABLE:
            drop_label.drop_target_register(DND_FILES)
            drop_label.dnd_bind("<<Drop>>", self._on_drop)
        else:
            drop_label.configure(text="Drag and drop requires tkinterdnd2.")

        buttons = ttk.Frame(drop_frame)
        buttons.grid(row=1, column=0, sticky="ew")
        ttk.Button(buttons, text="Add Files", command=self._add_files).pack(
            side="left", padx=4
        )
        ttk.Button(buttons, text="Clear", command=self._clear_files).pack(
            side="left"
        )

        self.file_list = tk.Listbox(drop_frame, height=5)
        self.file_list.grid(row=2, column=0, sticky="ew", pady=6)
        self.file_list.bind("<<ListboxSelect>>", self._on_select_file)

        output_frame = ttk.LabelFrame(main, text="Output", padding=8)
        output_frame.grid(row=1, column=0, sticky="ew", pady=8)
        output_frame.columnconfigure(1, weight=1)
        ttk.Label(output_frame, text="Output folder").grid(row=0, column=0, padx=4)
        output_entry = ttk.Entry(output_frame, textvariable=self.output_dir)
        output_entry.grid(row=0, column=1, sticky="ew")
        ttk.Button(output_frame, text="Browse", command=self._browse_output).grid(
            row=0, column=2, padx=4
        )

        options_frame = ttk.LabelFrame(main, text="Options", padding=8)
        options_frame.grid(row=2, column=0, sticky="ew")
        options_frame.columnconfigure(1, weight=1)
        ttk.Label(options_frame, text="Format").grid(row=0, column=0, padx=4)
        format_box = ttk.Combobox(
            options_frame,
            textvariable=self.format_var,
            values=["jpeg", "png", "webp"],
            state="readonly",
        )
        format_box.grid(row=0, column=1, sticky="w")
        format_box.bind("<<ComboboxSelected>>", self._on_option_change)

        ttk.Label(options_frame, text="Quality").grid(row=1, column=0, padx=4)
        quality_scale = ttk.Scale(
            options_frame,
            from_=1,
            to=100,
            variable=self.quality_var,
            command=lambda _value: self._on_option_change(),
        )
        quality_scale.grid(row=1, column=1, sticky="ew")
        self.quality_label = ttk.Label(options_frame, text="75")
        self.quality_label.grid(row=1, column=2, padx=4)

        self.optimize_check = ttk.Checkbutton(
            options_frame, text="Optimize PNG", variable=self.optimize_var
        )
        self.optimize_check.grid(row=2, column=1, sticky="w")

        preview_frame = ttk.LabelFrame(main, text="Preview", padding=8)
        preview_frame.grid(row=3, column=0, sticky="nsew", pady=8)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.columnconfigure(1, weight=1)

        self.original_canvas = ttk.Label(preview_frame, text="Original")
        self.original_canvas.grid(row=0, column=0, sticky="nsew", padx=4)
        self.compressed_canvas = ttk.Label(preview_frame, text="Compressed")
        self.compressed_canvas.grid(row=0, column=1, sticky="nsew", padx=4)

        action_frame = ttk.Frame(main)
        action_frame.grid(row=4, column=0, sticky="ew")
        action_frame.columnconfigure(0, weight=1)
        ttk.Button(action_frame, text="Compress", command=self._compress_all).pack(
            side="right"
        )

    def _add_files(self) -> None:
        file_paths = filedialog.askopenfilenames(
            title="Select images",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp *.gif")],
        )
        if file_paths:
            self._append_files([Path(path) for path in file_paths])

    def _on_drop(self, event: tk.Event) -> None:
        if not getattr(event, "data", None):
            return
        files = self._parse_drop_files(event.data)
        if files:
            self._append_files(files)

    def _parse_drop_files(self, data: str) -> list[Path]:
        raw_files = self.root.tk.splitlist(data)
        return [Path(path) for path in raw_files]

    def _append_files(self, files: Iterable[Path]) -> None:
        new_files = [path for path in files if path.exists()]
        if not new_files:
            return
        self.files.extend(new_files)
        for path in new_files:
            self.file_list.insert(tk.END, str(path))
        if len(self.files) == len(new_files):
            self.file_list.selection_set(0)
            self._update_preview(self.files[0])

    def _clear_files(self) -> None:
        self.files.clear()
        self.file_list.delete(0, tk.END)
        self.original_canvas.configure(image="", text="Original")
        self.compressed_canvas.configure(image="", text="Compressed")
        self.preview_images = PreviewImages()

    def _browse_output(self) -> None:
        directory = filedialog.askdirectory(title="Select output folder")
        if directory:
            self.output_dir.set(directory)

    def _on_select_file(self, _event: tk.Event) -> None:
        selection = self.file_list.curselection()
        if not selection:
            return
        index = selection[0]
        self._update_preview(self.files[index])

    def _on_option_change(self, _event: object | None = None) -> None:
        self.quality_label.configure(text=str(int(self.quality_var.get())))
        self.optimize_check.state(
            ["!disabled"]
            if self.format_var.get() == "png"
            else ["disabled"]
        )
        selection = self.file_list.curselection()
        if selection:
            self._update_preview(self.files[selection[0]])

    def _update_preview(self, path: Path) -> None:
        options = _validate_options(
            EncodeOptions(
                fmt=self.format_var.get(),
                quality=int(self.quality_var.get()),
                optimize=self.optimize_var.get(),
            )
        )
        original_image = self._load_preview_image(path)
        compressed_image = self._render_compressed_preview(path, options)
        if original_image is not None:
            self.preview_images.original = original_image
            self.original_canvas.configure(image=original_image, text="")
        if compressed_image is not None:
            self.preview_images.compressed = compressed_image
            self.compressed_canvas.configure(image=compressed_image, text="")

    def _load_preview_image(self, path: Path) -> object | None:
        pillow = self._load_pillow()
        if pillow is None:
            return None
        Image, ImageTk = pillow
        with Image.open(path) as image:
            image.load()
            image.thumbnail((260, 260))
            return ImageTk.PhotoImage(image)

    def _render_compressed_preview(
        self, path: Path, options: EncodeOptions
    ) -> object | None:
        pillow = self._load_pillow()
        if pillow is None:
            return None
        Image, ImageTk = pillow
        with Image.open(path) as image:
            image.load()
            buffer = io.BytesIO()
            save_kwargs: dict[str, object] = {}
            if options.fmt in {"jpeg", "jpg", "webp"}:
                save_kwargs["quality"] = options.quality
                save_kwargs["optimize"] = True
            if options.fmt == "png":
                save_kwargs["optimize"] = options.optimize
            image.save(buffer, format=options.fmt.upper(), **save_kwargs)
            buffer.seek(0)
            with Image.open(buffer) as preview_image:
                preview_image.load()
                preview_image.thumbnail((260, 260))
                return ImageTk.PhotoImage(preview_image)

    def _load_pillow(self):
        if importlib.util.find_spec("PIL") is None:
            messagebox.showerror(
                "Missing dependency", "Pillow is required. Install it first."
            )
            return None
        from PIL import Image, ImageTk  # type: ignore

        return Image, ImageTk

    def _compress_all(self) -> None:
        if not self.files:
            messagebox.showwarning("No files", "Please add image files first.")
            return
        output_base = Path(self.output_dir.get()).expanduser()
        options = _validate_options(
            EncodeOptions(
                fmt=self.format_var.get(),
                quality=int(self.quality_var.get()),
                optimize=self.optimize_var.get(),
            )
        )
        output_base.mkdir(parents=True, exist_ok=True)
        for path in self.files:
            output_name = f"{path.stem}.{self._format_extension(options.fmt)}"
            output_path = output_base / output_name
            _compress_image(path, output_path, options)
        messagebox.showinfo("Completed", f"Saved {len(self.files)} files.")

    @staticmethod
    def _format_extension(fmt: str) -> str:
        if fmt == "jpeg":
            return "jpg"
        return fmt


def main() -> None:
    if _DND_AVAILABLE:
        root = TkinterDnD.Tk()  # type: ignore
    else:
        root = tk.Tk()
    app = SquooshGUI(root)
    app._on_option_change()
    root.mainloop()


if __name__ == "__main__":
    if os.environ.get("TK_SILENCE_DEPRECATION") is None:
        os.environ["TK_SILENCE_DEPRECATION"] = "1"
    main()
