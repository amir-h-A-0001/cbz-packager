import os
import re
import shutil
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import customtkinter as ctk
from PIL import Image, ImageTk

# ---------------------------------------------------------------------------
# Theme configuration
# ---------------------------------------------------------------------------
COLORS = {
    "bg": "#0B1020",          # Main window background
    "surface": "#111C30",     # Panels / Card containers
    "surface_alt": "#16243B", # Inputs / list backgrounds
    "border": "#263753",
    "text": "#E6EDF8",
    "muted": "#91A2BC",
    "accent": "#477DDB",      # Primary blue
    "accent_hover": "#5B91F0",
    "accent_pressed": "#315FAE",
    "selection": "#244A83",
    "success": "#45C49A",
    "error": "#F07178",
}

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


def extract_number(text):
    """Extract the first number from text for sorting[cite: 3]."""
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    return float(match.group(1)) if match else 0


def extract_last_number(filename):
    """Extract the last number from filename for sorting[cite: 3]."""
    name_without_ext = os.path.splitext(filename)[0]
    numbers = re.findall(r"\d+", name_without_ext)
    return int(numbers[-1]) if numbers else 0


class ComicPackagerApp:
    IMAGE_EXTENSIONS = {
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Comic Archive Packager")
        self.root.geometry("1220x840")
        self.root.minsize(1050, 750)
        self.root.configure(fg_color=COLORS["bg"])

        self.source_dir = ""
        self.output_dir = ""
        self.chapter_data = {}
        self.current_selected_chapter = None
        self.current_preview_image = None

        self.create_widgets()

    def make_listbox(self, parent):
        """Creates a styled standard listbox with modern dark theme aesthetics[cite: 3]."""
        return tk.Listbox(
            parent,
            selectmode=tk.SINGLE,
            font=("Cascadia Code", 10),
            bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            selectbackground=COLORS["selection"],
            selectforeground="#FFFFFF",
            activestyle="none",
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
            exportselection=False,
        )

    def create_widgets(self):
        # Main container with responsive resizing
        main_layout = ctk.CTkFrame(self.root, fg_color=COLORS["bg"], corner_radius=0)
        main_layout.pack(fill="both", expand=True, padx=20, pady=16)
        main_layout.grid_columnconfigure(0, weight=1)
        main_layout.grid_rowconfigure(2, weight=1)

        # ---------------------------------------------------------------------------
        # A. Application Header[cite: 4]
        # ---------------------------------------------------------------------------
        header = ctk.CTkFrame(main_layout, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(4, 12))

        title_label = ctk.CTkLabel(
            header,
            text="Comic Archive Packager",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=COLORS["text"],
            anchor="w"
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            header,
            text="Organize chapters, reorder pages with live preview, and create CBZ archives[cite: 3, 4].",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["muted"],
            anchor="w"
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))

        # ---------------------------------------------------------------------------
        # B. Directory and Archive Settings[cite: 4]
        # ---------------------------------------------------------------------------
        path_frame = ctk.CTkFrame(
            main_layout,
            fg_color=COLORS["surface"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=12
        )
        path_frame.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        path_frame.grid_columnconfigure(1, weight=1)

        # Source Folder Row
        ctk.CTkLabel(
            path_frame,
            text="Source folder",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text"]
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 8))

        self.source_entry = ctk.CTkEntry(
            path_frame,
            fg_color=COLORS["surface_alt"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            placeholder_text="Select source directory...",
            corner_radius=8,
            height=34
        )
        self.source_entry.grid(row=0, column=1, sticky="ew", padx=8, pady=(14, 8))

        browse_source_btn = ctk.CTkButton(
            path_frame,
            text="Browse…",
            command=self.select_source,
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["border"],
            text_color=COLORS["text"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8,
            width=90,
            height=34
        )
        browse_source_btn.grid(row=0, column=2, padx=(8, 16), pady=(14, 8))

        # Archive Name Row
        ctk.CTkLabel(
            path_frame,
            text="Archive name",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text"]
        ).grid(row=0, column=3, sticky="w", padx=(12, 8), pady=(14, 8))

        self.name_entry = ctk.CTkEntry(
            path_frame,
            fg_color=COLORS["surface_alt"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            placeholder_text="Archive filename...",
            corner_radius=8,
            height=34,
            width=180
        )
        self.name_entry.grid(row=0, column=4, sticky="ew", padx=(0, 16), pady=(14, 8))

        # Output Folder Row
        ctk.CTkLabel(
            path_frame,
            text="Output folder",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text"]
        ).grid(row=1, column=0, sticky="w", padx=16, pady=(8, 14))

        self.output_entry = ctk.CTkEntry(
            path_frame,
            fg_color=COLORS["surface_alt"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            placeholder_text="Select destination directory...",
            corner_radius=8,
            height=34
        )
        self.output_entry.grid(row=1, column=1, sticky="ew", padx=8, pady=(8, 14))

        browse_output_btn = ctk.CTkButton(
            path_frame,
            text="Browse…",
            command=self.select_output,
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["border"],
            text_color=COLORS["text"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8,
            width=90,
            height=34
        )
        browse_output_btn.grid(row=1, column=2, padx=(8, 16), pady=(8, 14))

        # ---------------------------------------------------------------------------
        # C. Chapter, Image Reordering & Live Preview (3-Column Layout)[cite: 4]
        # ---------------------------------------------------------------------------
        reorder_frame = ctk.CTkFrame(main_layout, fg_color="transparent")
        reorder_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 12))
        reorder_frame.grid_columnconfigure((0, 1, 2), weight=1)
        reorder_frame.grid_rowconfigure(0, weight=1)

        # 1. Left Panel: Chapters / Subdirectories[cite: 4]
        chapter_frame = ctk.CTkFrame(
            reorder_frame,
            fg_color=COLORS["surface"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=12
        )
        chapter_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        chapter_frame.grid_columnconfigure(0, weight=1)
        chapter_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            chapter_frame,
            text="01  CHAPTERS",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=12),
            text_color=COLORS["text"],
            anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 6))

        chap_content_frame = ctk.CTkFrame(chapter_frame, fg_color="transparent")
        chap_content_frame.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        chap_content_frame.grid_columnconfigure(0, weight=1)
        chap_content_frame.grid_rowconfigure(0, weight=1)

        chap_list_container = ctk.CTkFrame(
            chap_content_frame,
            fg_color=COLORS["surface_alt"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8
        )
        chap_list_container.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        chap_list_container.grid_columnconfigure(0, weight=1)
        chap_list_container.grid_rowconfigure(0, weight=1)

        self.chap_listbox = self.make_listbox(chap_list_container)
        self.chap_listbox.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        
        chap_scrollbar = ctk.CTkScrollbar(
            chap_list_container,
            command=self.chap_listbox.yview,
            fg_color=COLORS["surface_alt"],
            button_color=COLORS["border"],
            button_hover_color=COLORS["muted"]
        )
        chap_scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 4), pady=4)
        self.chap_listbox.configure(yscrollcommand=chap_scrollbar.set)
        self.chap_listbox.bind("<<ListboxSelect>>", self.on_chapter_select)

        chap_btn_frame = ctk.CTkFrame(chap_content_frame, fg_color="transparent")
        chap_btn_frame.grid(row=0, column=1, sticky="ns")

        ctk.CTkButton(
            chap_btn_frame,
            text="▲ Up",
            command=self.move_chapter_up,
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["border"],
            text_color=COLORS["text"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8,
            width=65,
            height=34
        ).pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            chap_btn_frame,
            text="▼ Down",
            command=self.move_chapter_down,
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["border"],
            text_color=COLORS["text"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8,
            width=65,
            height=34
        ).pack(fill="x")

        # 2. Middle Panel: Pages in Selected Chapter[cite: 4]
        image_frame = ctk.CTkFrame(
            reorder_frame,
            fg_color=COLORS["surface"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=12
        )
        image_frame.grid(row=0, column=1, sticky="nsew", padx=6)
        image_frame.grid_columnconfigure(0, weight=1)
        image_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            image_frame,
            text="02  PAGES",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=12),
            text_color=COLORS["text"],
            anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 6))

        img_content_frame = ctk.CTkFrame(image_frame, fg_color="transparent")
        img_content_frame.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        img_content_frame.grid_columnconfigure(0, weight=1)
        img_content_frame.grid_rowconfigure(0, weight=1)

        img_list_container = ctk.CTkFrame(
            img_content_frame,
            fg_color=COLORS["surface_alt"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8
        )
        img_list_container.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        img_list_container.grid_columnconfigure(0, weight=1)
        img_list_container.grid_rowconfigure(0, weight=1)

        self.img_listbox = self.make_listbox(img_list_container)
        self.img_listbox.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self.img_listbox.bind("<<ListboxSelect>>", self.on_image_select)

        img_scrollbar = ctk.CTkScrollbar(
            img_list_container,
            command=self.img_listbox.yview,
            fg_color=COLORS["surface_alt"],
            button_color=COLORS["border"],
            button_hover_color=COLORS["muted"]
        )
        img_scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 4), pady=4)
        self.img_listbox.configure(yscrollcommand=img_scrollbar.set)

        img_btn_frame = ctk.CTkFrame(img_content_frame, fg_color="transparent")
        img_btn_frame.grid(row=0, column=1, sticky="ns")

        ctk.CTkButton(
            img_btn_frame,
            text="▲ Up",
            command=self.move_image_up,
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["border"],
            text_color=COLORS["text"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8,
            width=65,
            height=34
        ).pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            img_btn_frame,
            text="▼ Down",
            command=self.move_image_down,
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["border"],
            text_color=COLORS["text"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8,
            width=65,
            height=34
        ).pack(fill="x")

        # 3. Right Panel: Live Image Preview
        preview_frame = ctk.CTkFrame(
            reorder_frame,
            fg_color=COLORS["surface"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=12
        )
        preview_frame.grid(row=0, column=2, sticky="nsew", padx=(6, 0))
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            preview_frame,
            text="03  LIVE PREVIEW",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=12),
            text_color=COLORS["text"],
            anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 6))

        preview_container = ctk.CTkFrame(
            preview_frame,
            fg_color=COLORS["surface_alt"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8
        )
        preview_container.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        preview_container.grid_columnconfigure(0, weight=1)
        preview_container.grid_rowconfigure(0, weight=1)

        self.preview_image_label = ctk.CTkLabel(
            preview_container,
            text="Select an image\nto preview",
            text_color=COLORS["muted"],
            font=ctk.CTkFont(family="Segoe UI", size=11)
        )
        self.preview_image_label.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        # ---------------------------------------------------------------------------
        # D. Processing Options & E. Process Action Button[cite: 4]
        # ---------------------------------------------------------------------------
        bottom_frame = ctk.CTkFrame(main_layout, fg_color="transparent")
        bottom_frame.grid(row=3, column=0, sticky="ew", pady=(0, 12))
        bottom_frame.grid_columnconfigure(0, weight=1)

        options_frame = ctk.CTkFrame(
            bottom_frame,
            fg_color=COLORS["surface"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=12
        )
        options_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))

        ctk.CTkLabel(
            options_frame,
            text="PROCESSING OPTIONS",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=12),
            text_color=COLORS["text"],
            anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 6), columnspan=4)

        self.pad_var = ctk.BooleanVar(value=True)
        pad_chk = ctk.CTkCheckBox(
            options_frame,
            text="Zero-padded numbering (001-001.jpg)",
            variable=self.pad_var,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            border_color=COLORS["border"]
        )
        pad_chk.grid(row=1, column=0, sticky="w", padx=14, pady=4, columnspan=4)

        self.cbz_var = ctk.BooleanVar(value=True)
        cbz_chk = ctk.CTkCheckBox(
            options_frame,
            text="Create .cbz archive after processing",
            variable=self.cbz_var,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            border_color=COLORS["border"]
        )
        cbz_chk.grid(row=2, column=0, sticky="w", padx=14, pady=4, columnspan=4)

        # Trimming inputs
        ctk.CTkLabel(
            options_frame,
            text="Trim start",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["muted"]
        ).grid(row=3, column=0, sticky="w", padx=(14, 6), pady=(8, 14))

        self.trim_start_entry = ctk.CTkEntry(
            options_frame,
            fg_color=COLORS["surface_alt"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            corner_radius=8,
            width=65,
            height=30
        )
        self.trim_start_entry.insert(0, "0")
        self.trim_start_entry.grid(row=3, column=1, sticky="w", padx=(0, 16), pady=(8, 14))

        ctk.CTkLabel(
            options_frame,
            text="Trim end",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["muted"]
        ).grid(row=3, column=2, sticky="w", padx=(0, 6), pady=(8, 14))

        self.trim_end_entry = ctk.CTkEntry(
            options_frame,
            fg_color=COLORS["surface_alt"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            corner_radius=8,
            width=65,
            height=30
        )
        self.trim_end_entry.insert(0, "0")
        self.trim_end_entry.grid(row=3, column=3, sticky="w", padx=(0, 14), pady=(8, 14))

        # Process Button Container
        process_container = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        process_container.pack(side="right", fill="y", padx=(8, 0))

        self.process_btn = ctk.CTkButton(
            process_container,
            text="Process & Pack  →",
            command=self.run_process,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=13),
            corner_radius=12,
            height=110,
            width=180
        )
        self.process_btn.pack(fill="both", expand=True)

        # ---------------------------------------------------------------------------
        # F. Activity Log[cite: 4]
        # ---------------------------------------------------------------------------
        log_frame = ctk.CTkFrame(
            main_layout,
            fg_color=COLORS["surface"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=12
        )
        log_frame.grid(row=4, column=0, sticky="ew")
        log_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            log_frame,
            text="LIVE ACTIVITY",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=12),
            text_color=COLORS["text"],
            anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 6))

        log_container = ctk.CTkFrame(
            log_frame,
            fg_color="#080F1C",
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8
        )
        log_container.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        log_container.grid_columnconfigure(0, weight=1)
        log_container.grid_rowconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(
            log_container,
            height=5,
            font=("Cascadia Code", 9),
            bg="#080F1C",
            fg="#B9C9E2",
            insertbackground=COLORS["text"],
            selectbackground=COLORS["selection"],
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            padx=10,
            pady=8,
            state="disabled",
        )
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.log_text.tag_configure("success", foreground=COLORS["success"])
        self.log_text.tag_configure("error", foreground=COLORS["error"])
        self.log_text.tag_configure("info", foreground="#9DBCF2")

    def log(self, message):
        self.log_text.configure(state="normal")
        tag = "info"
        if "ERROR" in message:
            tag = "error"
        elif "successfully" in message.lower() or "successfully" in message:
            tag = "success"

        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")
        self.root.update_idletasks()

    def select_source(self):
        dir_path = filedialog.askdirectory(title="Select source folder")
        if dir_path:
            self.source_dir = dir_path
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, dir_path)

            folder_name = os.path.basename(os.path.normpath(dir_path))
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, folder_name)

            if not self.output_dir:
                self.output_dir = dir_path
                self.output_entry.delete(0, tk.END)
                self.output_entry.insert(0, dir_path)

            self.load_directory_structure()

    def select_output(self):
        dir_path = filedialog.askdirectory(title="Select output folder")
        if dir_path:
            self.output_dir = dir_path
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, dir_path)

    def load_directory_structure(self):
        self.chap_listbox.delete(0, tk.END)
        self.img_listbox.delete(0, tk.END)
        self.chapter_data = {}
        self.current_selected_chapter = None
        self.clear_preview()

        try:
            items = os.listdir(self.source_dir)
            dirs = [
                item for item in items
                if os.path.isdir(os.path.join(self.source_dir, item))
            ]
            dirs.sort(key=extract_number)

            for directory in dirs:
                directory_path = os.path.join(self.source_dir, directory)
                images = [
                    filename for filename in os.listdir(directory_path)
                    if os.path.isfile(os.path.join(directory_path, filename))
                    and os.path.splitext(filename)[1].lower()
                    in self.IMAGE_EXTENSIONS
                ]
                images.sort(key=extract_last_number)
                self.chapter_data[directory] = images
                self.chap_listbox.insert(tk.END, directory)

            self.log(f"Loaded source: {self.source_dir}")
            self.log(f"Found {len(dirs)} subdirectories.")

            if dirs:
                self.chap_listbox.selection_set(0)
                self.on_chapter_select(None)

        except Exception as exc:
            messagebox.showerror(
                "Directory Error",
                f"Could not read directory:\n{exc}",
                parent=self.root,
            )

    def on_chapter_select(self, event):
        selection = self.chap_listbox.curselection()
        if not selection:
            return

        chapter_name = self.chap_listbox.get(selection[0])
        self.current_selected_chapter = chapter_name

        self.img_listbox.delete(0, tk.END)
        images = self.chapter_data.get(chapter_name, [])
        for image in images:
            self.img_listbox.insert(tk.END, image)

        self.clear_preview()
        if images:
            self.img_listbox.selection_set(0)
            self.on_image_select(None)

    def on_image_select(self, event):
        if not self.current_selected_chapter:
            return
        selection = self.img_listbox.curselection()
        if not selection:
            return

        image_filename = self.img_listbox.get(selection[0])
        image_path = os.path.join(self.source_dir, self.current_selected_chapter, image_filename)

        try:
            pil_img = Image.open(image_path)
            # Resize nicely to fit preview container bounds (max width ~220, max height ~260)
            pil_img.thumbnail((220, 260), Image.Resampling.LANCZOS)
            self.current_preview_image = ImageTk.PhotoImage(pil_img)
            self.preview_image_label.configure(image=self.current_preview_image, text="")
        except Exception:
            self.clear_preview("Preview unavailable")

    def clear_preview(self, text="Select an image\nto preview"):
        self.current_preview_image = None
        self.preview_image_label.configure(image="", text=text)

    def move_chapter_up(self):
        selection = self.chap_listbox.curselection()
        if not selection or selection[0] == 0:
            return

        index = selection[0]
        item = self.chap_listbox.get(index)
        self.chap_listbox.delete(index)
        self.chap_listbox.insert(index - 1, item)
        self.chap_listbox.selection_set(index - 1)
        self.chap_listbox.activate(index - 1)

    def move_chapter_down(self):
        selection = self.chap_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        if index >= self.chap_listbox.size() - 1:
            return

        item = self.chap_listbox.get(index)
        self.chap_listbox.delete(index)
        self.chap_listbox.insert(index + 1, item)
        self.chap_listbox.selection_set(index + 1)
        self.chap_listbox.activate(index + 1)

    def move_image_up(self):
        if not self.current_selected_chapter:
            return

        selection = self.img_listbox.curselection()
        if not selection or selection[0] == 0:
            return

        index = selection[0]
        item = self.img_listbox.get(index)
        self.img_listbox.delete(index)
        self.img_listbox.insert(index - 1, item)
        self.img_listbox.selection_set(index - 1)
        self.img_listbox.activate(index - 1)

        images = self.chapter_data[self.current_selected_chapter]
        images.insert(index - 1, images.pop(index))

    def move_image_down(self):
        if not self.current_selected_chapter:
            return

        selection = self.img_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        if index >= self.img_listbox.size() - 1:
            return

        item = self.img_listbox.get(index)
        self.img_listbox.delete(index)
        self.img_listbox.insert(index + 1, item)
        self.img_listbox.selection_set(index + 1)
        self.img_listbox.activate(index + 1)

        images = self.chapter_data[self.current_selected_chapter]
        images.insert(index + 1, images.pop(index))

    def run_process(self):
        # Read the visible fields so edits made directly in the entries apply[cite: 3].
        self.source_dir = self.source_entry.get().strip()
        self.output_dir = self.output_entry.get().strip()

        if not self.source_dir or not self.output_dir:
            messagebox.showwarning(
                "Missing information",
                "Please select source and output folders.",
                parent=self.root,
            )
            return

        ordered_chapters = list(self.chap_listbox.get(0, tk.END))
        if not ordered_chapters:
            messagebox.showwarning(
                "No data", "No chapters found to process.", parent=self.root
            )
            return

        try:
            trim_start = int(self.trim_start_entry.get().strip() or 0)
            trim_end = int(self.trim_end_entry.get().strip() or 0)
            if trim_start < 0 or trim_end < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Invalid trimming values",
                "Trim values must be non-negative whole numbers.",
                parent=self.root,
            )
            return

        try:
            os.makedirs(self.output_dir, exist_ok=True)
            total_images = 0
            self.log("\n--- Starting processing ---")

            for chapter_index, chapter_name in enumerate(
                ordered_chapters, start=1
            ):
                chapter_path = os.path.join(self.source_dir, chapter_name)
                images = list(self.chapter_data.get(chapter_name, []))

                if trim_start:
                    images = images[trim_start:]
                if trim_end:
                    images = images[:-trim_end] if trim_end < len(images) else []

                if not images:
                    self.log(
                        f"Chapter {chapter_index}: {chapter_name} skipped "
                        "(empty after trimming)."
                    )
                    continue

                self.log(
                    f"Processing chapter {chapter_index}: {chapter_name} "
                    f"({len(images)} pages)"
                )

                for page_index, image_file in enumerate(images, start=1):
                    extension = os.path.splitext(image_file)[1]
                    if self.pad_var.get():
                        new_name = (
                            f"{chapter_index:03d}-{page_index:03d}{extension}"
                        )
                    else:
                        new_name = f"{chapter_index}-{page_index}{extension}"

                    source_path = os.path.join(chapter_path, image_file)
                    destination_path = os.path.join(self.output_dir, new_name)
                    shutil.copy2(source_path, destination_path)
                    total_images += 1

            self.log(
                f"✓ Successfully copied and renamed {total_images} images."
            )

            if self.cbz_var.get():
                archive_name = self.name_entry.get().strip()
                if not archive_name:
                    archive_name = os.path.basename(
                        os.path.normpath(self.source_dir)
                    )
                if not archive_name.lower().endswith(".cbz"):
                    archive_name += ".cbz"

                archive_path = os.path.join(
                    os.path.dirname(self.output_dir), archive_name
                )
                self.log(f"Creating CBZ archive: {archive_path}")

                output_images = sorted(
                    filename for filename in os.listdir(self.output_dir)
                    if os.path.splitext(filename)[1].lower()
                    in self.IMAGE_EXTENSIONS
                )

                with zipfile.ZipFile(
                    archive_path, "w", compression=zipfile.ZIP_STORED
                ) as archive:
                    for filename in output_images:
                        archive.write(
                            os.path.join(self.output_dir, filename), filename
                        )

                self.log("✓ CBZ archive created successfully!")

            messagebox.showinfo(
                "Complete",
                f"Successfully processed {total_images} images!",
                parent=self.root,
            )

        except Exception as exc:
            self.log(f"ERROR: {exc}")
            messagebox.showerror(
                "Processing error",
                f"An error occurred:\n{exc}",
                parent=self.root,
            )


if __name__ == "__main__":
    root = ctk.CTk()
    app = ComicPackagerApp(root)
    root.mainloop()