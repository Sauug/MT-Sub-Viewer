import tkinter as tk
from tkinter import ttk
from pathlib import Path
from PIL import Image, ImageTk, ImageDraw

# ====== CONFIG ======
DDS_PATH = Path(r"YOUR_PATH_DDS_FILE")
DDS_NAME = DDS_PATH.name

SUB_ROOT = Path(r"YOUR_PATH_TO_SCAN_SUB_FILE")
# =====================


def parse_sub(path: Path):
    coords = {}
    image_name = None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            if parts[0] == "image" and len(parts) >= 2:
                val = " ".join(parts[1:])
                image_name = val.strip().strip('"')
            elif parts[0] in ("left", "top", "right", "bottom") and len(parts) >= 2:
                coords[parts[0]] = int(parts[1])
    return coords, image_name


def find_sub_files_for_dds(root: Path, dds_name: str):
    result = []
    for sub_path in root.rglob("*.sub"):
        _, img_name = parse_sub(sub_path)
        if img_name == dds_name:
            result.append(sub_path)
    return result


class SubViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"SUB viewer - {DDS_NAME}")

        tk.Label(self, text=f"DDS: {DDS_PATH}").pack(pady=2)
        tk.Label(self, text=f"Scan SUB root: {SUB_ROOT}", fg="gray").pack(pady=2)

        self.base_img = Image.open(DDS_PATH)
        self.tk_img = None

        self.label = tk.Label(self)
        self.label.pack()

        self.sub_files = find_sub_files_for_dds(SUB_ROOT, DDS_NAME)
        if not self.sub_files:
            print("Aucun .sub trouvé pour", DDS_NAME, "sous", SUB_ROOT)

        self.sub_names = [str(p.relative_to(SUB_ROOT)) for p in self.sub_files]

        frame = tk.Frame(self)
        frame.pack(pady=5)

        tk.Label(frame, text="SUB:").pack(side=tk.LEFT)

        self.sub_var = tk.StringVar()
        if self.sub_names:
            self.sub_var.set(self.sub_names[0])

        self.combo = ttk.Combobox(
            frame,
            textvariable=self.sub_var,
            values=self.sub_names,
            state="readonly",
            width=80,
        )
        self.combo.pack(side=tk.LEFT)
        self.combo.bind("<<ComboboxSelected>>", lambda e: self.update_image())

        self.current_sub_label = tk.Label(self, text="", fg="gray")
        self.current_sub_label.pack(pady=2)

        # boutons précédent / suivant
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)

        btn_prev = tk.Button(btn_frame, text="Prev SUB (P)", command=self.prev_sub)
        btn_prev.pack(side=tk.LEFT, padx=5)

        btn_next = tk.Button(btn_frame, text="Next SUB (N)", command=self.next_sub)
        btn_next.pack(side=tk.LEFT, padx=5)

        # raccourcis clavier
        self.bind("<r>", lambda e: self.update_image())
        self.bind("<n>", lambda e: self.next_sub())
        self.bind("<p>", lambda e: self.prev_sub())

        self.update_image()


    def get_current_index(self):
        if not self.sub_names:
            return -1
        current = self.sub_var.get()
        try:
            return self.sub_names.index(current)
        except ValueError:
            return 0

    def next_sub(self):
        if not self.sub_names:
            return
        idx = self.get_current_index()
        idx = (idx + 1) % len(self.sub_names)
        self.sub_var.set(self.sub_names[idx])
        self.update_image()

    def prev_sub(self):
        if not self.sub_names:
            return
        idx = self.get_current_index()
        idx = (idx - 1) % len(self.sub_names)
        self.sub_var.set(self.sub_names[idx])
        self.update_image()

    def update_image(self):
        if not self.sub_names or not self.sub_var.get():
            return

        rel = self.sub_var.get()
        sub_path = SUB_ROOT / rel

        self.current_sub_label.config(text=f"Fichier SUB actuel : {sub_path}")

        coords, img_name = parse_sub(sub_path)
        print("=== update_image with", sub_path)
        print("image =", img_name, "coords =", coords)

        if not all(k in coords for k in ("left", "top", "right", "bottom")):
            print("SUB incomplet, manque coords")
            return

        img = self.base_img.copy()
        draw = ImageDraw.Draw(img)

        left = coords["left"]
        top = coords["top"]
        right = coords["right"]
        bottom = coords["bottom"]

        draw.rectangle([(left, top), (right, bottom)], outline="red", width=2)

        self.tk_img = ImageTk.PhotoImage(img)
        self.label.config(image=self.tk_img)


if __name__ == "__main__":
    app = SubViewer()
    app.mainloop()
