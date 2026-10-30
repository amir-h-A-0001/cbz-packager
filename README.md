# Comic Archive Packager (`cbz-packager`)

A modern desktop application built with Python and CustomTkinter designed to organize, reorder, preview, trim, and package scattered chapter/volume image folders into clean, sequential `.cbz` (Comic Book Archive) files.

---

## ✨ Key Features

* **Modern Dark-Blue SaaS GUI:** Designed with a polished CustomTkinter dark theme, rounded cards, and a clean layout inspired by modern web tools.
* **Intelligent Natural Sorting:** Automatically sorts chapter subdirectories using the first number found in their names (`extract_number`) and sorts individual pages using the last number in their filenames (`extract_last_number`).
* **Interactive Dual Reordering:** Includes side-by-side listboxes with Up/Down buttons to manually reorder both entire chapters and individual pages within chapters.
* **Live Image Preview:** Instantly displays a thumbnail preview of any selected page so you can easily identify what you are moving.
* **Page Trimming:** Easily strip unwanted cover art, credits, or scanlation team notes by setting custom start and end page trim values for chapters.
* **Flexible Numbering Formats:** Choose between standard numbering or zero-padded sequential naming (e.g., `001-001.jpg`).
* **Live Activity Console:** Real-time log output with color-coded feedback tracking every file copy, rename, and archive creation step.
* **Automated `.cbz` Packager:** Bundles the flattened, processed images directly into a standard comic book archive zip file.

---

## 🛠️ Requirements & Installation

1. **Python 3.10+** installed on your system.
2. Install the required dependencies (`customtkinter` and `Pillow`):
   ```bash
   pip install customtkinter pillow
   ```

---

## 🚀 How to Use

1. Clone or download this repository:
   ```bash
   git clone https://github.com/amir-h-A-0001/cbz-packager.git
   cd cbz-packager
   ```
2. Run the application script:
   ```bash
   python gui.py
   ```
3. **In the Application:**
   * **Source Folder:** Select the root directory containing your chapter/volume subfolders.
   * **Archive Name:** Customize the filename for your output `.cbz` archive.
   * **Output Folder:** Choose where the processed images will be saved.
   * **Reorder & Preview:** Click through chapters and pages to adjust their sequence or inspect them via the live image preview panel.
   * **Options:** Configure zero-padding or page trimming parameters if needed.
   * **Process & Pack:** Click the primary conversion button to flatten, rename, and package your comic.

---

## 📁 Project Structure

* `gui.py` — The primary CustomTkinter graphical user interface application with live preview, reordering, trimming, and logging features.
* `convert.py` — Core backend utility logic handling file parsing, natural sorting, image copying, and CBZ zip compression.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.