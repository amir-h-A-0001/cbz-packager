import os
import shutil
import re
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext

def extract_number(text):
    """Extract the first number from text for sorting"""
    match = re.search(r'(\d+(?:\.\d+)?)', text)
    if match:
        return float(match.group(1))
    return 0

def extract_last_number(filename):
    """Extract the last number from filename for sorting"""
    name_without_ext = os.path.splitext(filename)[0]
    numbers = re.findall(r'\d+', name_without_ext)
    if numbers:
        return int(numbers[-1])
    return 0

class ComicPackagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Comic Archive Packager")
        self.root.geometry("900x760")
        self.root.minsize(850, 700)

        self.source_dir = ""
        self.output_dir = ""
        
        # Data structure: { "ChapterName": [list of image filenames], ... }
        self.chapter_data = {} 
        self.current_selected_chapter = None

        self.create_widgets()

    def create_widgets(self):
        # --- PATH & NAME SELECTION FRAME ---
        path_frame = ttk.LabelFrame(self.root, text=" Directories & Archive Settings ", padding=10)
        path_frame.pack(fill="x", padx=10, pady=5)

        # Row 0: Source Folder & Archive Name (Top Right)
        ttk.Label(path_frame, text="Source Folder:").grid(row=0, column=0, sticky="w", pady=2)
        self.source_entry = ttk.Entry(path_frame, width=42)
        self.source_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(path_frame, text="Browse...", command=self.select_source).grid(row=0, column=2, pady=2, padx=(0, 20))

        ttk.Label(path_frame, text="Archive Name:").grid(row=0, column=3, sticky="w", pady=2)
        self.name_entry = ttk.Entry(path_frame, width=22)
        self.name_entry.grid(row=0, column=4, padx=5, pady=2)

        # Row 1: Output Folder
        ttk.Label(path_frame, text="Output Folder:").grid(row=1, column=0, sticky="w", pady=2)
        self.output_entry = ttk.Entry(path_frame, width=42)
        self.output_entry.grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(path_frame, text="Browse...", command=self.select_output).grid(row=1, column=2, pady=2, padx=(0, 20))

        # --- REORDERING FRAME (TWO COLUMNS: CHAPTERS & IMAGES) ---
        reorder_main_frame = ttk.Frame(self.root)
        reorder_main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Left Column: Chapters
        chap_frame = ttk.LabelFrame(reorder_main_frame, text=" 1. Chapters / Subdirectories (Reorder) ", padding=5)
        chap_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        chap_container = ttk.Frame(chap_frame)
        chap_container.pack(side="left", fill="both", expand=True)
        self.chap_listbox = tk.Listbox(chap_container, selectmode=tk.SINGLE, font=("Courier", 9))
        chap_scroll = ttk.Scrollbar(chap_container, orient="vertical", command=self.chap_listbox.yview)
        self.chap_listbox.configure(yscrollcommand=chap_scroll.set)
        self.chap_listbox.pack(side="left", fill="both", expand=True)
        chap_scroll.pack(side="right", fill="y")
        self.chap_listbox.bind('<<ListboxSelect>>', self.on_chapter_select)

        chap_btn_frame = ttk.Frame(chap_frame)
        chap_btn_frame.pack(side="right", fill="y", padx=5)
        ttk.Button(chap_btn_frame, text="▲ Up", command=self.move_chapter_up).pack(fill="x", pady=2)
        ttk.Button(chap_btn_frame, text="▼ Down", command=self.move_chapter_down).pack(fill="x", pady=2)

        # Right Column: Images inside selected chapter
        img_frame = ttk.LabelFrame(reorder_main_frame, text=" 2. Pictures in Selected Chapter (Reorder) ", padding=5)
        img_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        img_container = ttk.Frame(img_frame)
        img_container.pack(side="left", fill="both", expand=True)
        self.img_listbox = tk.Listbox(img_container, selectmode=tk.SINGLE, font=("Courier", 9))
        img_scroll = ttk.Scrollbar(img_container, orient="vertical", command=self.img_listbox.yview)
        self.img_listbox.configure(yscrollcommand=img_scroll.set)
        self.img_listbox.pack(side="left", fill="both", expand=True)
        img_scroll.pack(side="right", fill="y")

        img_btn_frame = ttk.Frame(img_frame)
        img_btn_frame.pack(side="right", fill="y", padx=5)
        ttk.Button(img_btn_frame, text="▲ Up", command=self.move_image_up).pack(fill="x", pady=2)
        ttk.Button(img_btn_frame, text="▼ Down", command=self.move_image_down).pack(fill="x", pady=2)

        # --- OPTIONS & LOGS FRAME ---
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill="x", padx=10, pady=5)

        options_frame = ttk.LabelFrame(bottom_frame, text=" Options ", padding=10)
        options_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.pad_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Zero-padded numbering (e.g., 001-001.jpg)", variable=self.pad_var).pack(anchor="w", pady=2)

        self.cbz_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Create .cbz Archive after processing", variable=self.cbz_var).pack(anchor="w", pady=2)

        # Page Trimming Sub-frame
        trim_frame = ttk.Frame(options_frame)
        trim_frame.pack(anchor="w", pady=5, fill="x")
        
        ttk.Label(trim_frame, text="Trim Start:").grid(row=0, column=0, sticky="w", padx=(0,5))
        self.trim_start_entry = ttk.Entry(trim_frame, width=5)
        self.trim_start_entry.insert(0, "0")
        self.trim_start_entry.grid(row=0, column=1, padx=(0, 15))

        ttk.Label(trim_frame, text="Trim End:").grid(row=0, column=2, sticky="w", padx=(0,5))
        self.trim_end_entry = ttk.Entry(trim_frame, width=5)
        self.trim_end_entry.insert(0, "0")
        self.trim_end_entry.grid(row=0, column=3)

        self.process_btn = ttk.Button(bottom_frame, text="Process & Pack", command=self.run_process)
        self.process_btn.pack(side="right", fill="both", padx=(5, 0), ipadx=10)

        # --- LOG CONSOLE ---
        log_frame = ttk.LabelFrame(self.root, text=" Live Activity Logs ", padding=5)
        log_frame.pack(fill="both", expand=False, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=6, font=("Courier", 8), state="disabled")
        self.log_text.pack(fill="both", expand=True)

    def log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")
        self.root.update_idletasks()

    def select_source(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.source_dir = dir_path
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, dir_path)
            
            # Auto-populate archive name based on folder name
            folder_name = os.path.basename(dir_path)
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, folder_name)
            
            if not self.output_dir:
                self.output_dir = dir_path
                self.output_entry.delete(0, tk.END)
                self.output_entry.insert(0, dir_path)

            self.load_directory_structure()

    def select_output(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_dir = dir_path
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, dir_path)

    def load_directory_structure(self):
        self.chap_listbox.delete(0, tk.END)
        self.img_listbox.delete(0, tk.END)
        self.chapter_data = {}
        
        try:
            items = os.listdir(self.source_dir)
            dirs = [item for item in items if os.path.isdir(os.path.join(self.source_dir, item))]
            dirs.sort(key=extract_number)  #[cite: 1]

            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}

            for d in dirs:
                d_path = os.path.join(self.source_dir, d)
                images = [f for f in os.listdir(d_path) if os.path.isfile(os.path.join(d_path, f)) and os.path.splitext(f)[1].lower() in image_extensions]
                images.sort(key=extract_last_number)  #[cite: 1]
                self.chapter_data[d] = images
                self.chap_listbox.insert(tk.END, d)

            self.log(f"Loaded source: {self.source_dir}")
            self.log(f"Found {len(dirs)} subdirectories.")
            if dirs:
                self.chap_listbox.selection_set(0)
                self.on_chapter_select(None)
        except Exception as e:
            messagebox.showerror("Error", f"Could not read directory:\n{e}")

    def on_chapter_select(self, event):
        try:
            selection = self.chap_listbox.curselection()
            if not selection:
                return
            idx = selection[0]
            chap_name = self.chap_listbox.get(idx)
            self.current_selected_chapter = chap_name
            
            self.img_listbox.delete(0, tk.END)
            for img in self.chapter_data.get(chap_name, []):
                self.img_listbox.insert(tk.END, img)
        except IndexError:
            pass

    def move_chapter_up(self):
        try:
            idx = self.chap_listbox.curselection()[0]
            if idx == 0: return
            text = self.chap_listbox.get(idx)
            self.chap_listbox.delete(idx)
            self.chap_listbox.insert(idx - 1, text)
            self.chap_listbox.selection_set(idx - 1)
        except IndexError:
            pass

    def move_chapter_down(self):
        try:
            idx = self.chap_listbox.curselection()[0]
            if idx == self.chap_listbox.size() - 1: return
            text = self.chap_listbox.get(idx)
            self.chap_listbox.delete(idx)
            self.chap_listbox.insert(idx + 1, text)
            self.chap_listbox.selection_set(idx + 1)
        except IndexError:
            pass

    def move_image_up(self):
        try:
            if not self.current_selected_chapter: return
            idx = self.img_listbox.curselection()[0]
            if idx == 0: return
            
            text = self.img_listbox.get(idx)
            self.img_listbox.delete(idx)
            self.img_listbox.insert(idx - 1, text)
            self.img_listbox.selection_set(idx - 1)
            
            img_list = self.chapter_data[self.current_selected_chapter]
            img_list.insert(idx - 1, img_list.pop(idx))
        except IndexError:
            pass

    def move_image_down(self):
        try:
            if not self.current_selected_chapter: return
            idx = self.img_listbox.curselection()[0]
            if idx == self.img_listbox.size() - 1: return
            
            text = self.img_listbox.get(idx)
            self.img_listbox.delete(idx)
            self.img_listbox.insert(idx + 1, text)
            self.img_listbox.selection_set(idx + 1)
            
            img_list = self.chapter_data[self.current_selected_chapter]
            img_list.insert(idx + 1, img_list.pop(idx))
        except IndexError:
            pass

    def run_process(self):
        if not self.source_dir or not self.output_dir:
            messagebox.showwarning("Missing Info", "Please select source and output folders.")
            return

        ordered_chapters = list(self.chap_listbox.get(0, tk.END))
        if not ordered_chapters:
            messagebox.showwarning("No Data", "No chapters found to process.")
            return

        # Read trim values safely
        try:
            trim_start = int(self.trim_start_entry.get().strip() or 0)
        except ValueError:
            trim_start = 0

        try:
            trim_end = int(self.trim_end_entry.get().strip() or 0)
        except ValueError:
            trim_end = 0

        try:
            os.makedirs(self.output_dir, exist_ok=True)
            total_images = 0
            self.log("\n--- Starting Processing ---")

            for dir_index, dir_name in enumerate(ordered_chapters, start=1):
                dir_path = os.path.join(self.source_dir, dir_name)
                images = list(self.chapter_data.get(dir_name, []))

                if not images:
                    continue

                # Apply page trimming options per chapter
                if trim_start > 0:
                    images = images[trim_start:]
                if trim_end > 0:
                    images = images[:-trim_end] if trim_end < len(images) else []

                if not images:
                    self.log(f"Chapter {dir_index}: {dir_name} skipped (empty after trimming).")
                    continue

                self.log(f"Processing Chapter {dir_index}: {dir_name} ({len(images)} pages after trim)")

                for pic_index, image_file in enumerate(images, start=1):
                    ext = os.path.splitext(image_file)[1]
                    
                    if self.pad_var.get():
                        new_name = f"{dir_index:03d}-{pic_index:03d}{ext}"
                    else:
                        new_name = f"{dir_index}-{pic_index}{ext}"
                    
                    source_path = os.path.join(dir_path, image_file)
                    dest_path = os.path.join(self.output_dir, new_name)
                    
                    shutil.copy2(source_path, dest_path)
                    total_images += 1

            self.log(f"✓ Successfully copied and renamed {total_images} images.")

            # Create CBZ if checked
            if self.cbz_var.get():
                custom_name = self.name_entry.get().strip()
                if not custom_name:
                    custom_name = os.path.basename(self.source_dir)
                if not custom_name.endswith('.cbz'):
                    custom_name += '.cbz'
                
                cbz_path = os.path.join(os.path.dirname(self.output_dir), custom_name)
                
                self.log(f"Creating CBZ archive: {cbz_path}")
                image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
                all_output_images = sorted([f for f in os.listdir(self.output_dir) if os.path.splitext(f)[1].lower() in image_extensions])
                
                with zipfile.ZipFile(cbz_path, 'w', zipfile.ZIP_STORED) as cbz:
                    for img in all_output_images:
                        cbz.write(os.path.join(self.output_dir, img), img)
                self.log(f"✓ CBZ archive created successfully!")

            messagebox.showinfo("Complete", f"Successfully processed {total_images} images!")

        except Exception as e:
            self.log(f"ERROR: {e}")
            messagebox.showerror("Error", f"An error occurred:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ComicPackagerApp(root)
    root.mainloop()