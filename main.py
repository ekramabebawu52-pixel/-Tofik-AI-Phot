import os
from datetime import datetime

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button

from PIL import Image as PILImage
from PIL import ImageEnhance, ImageFilter, ImageOps, ImageDraw

from plyer import filechooser


KV = r"""
<EditorUI>:
    orientation: "vertical"
    padding: "12dp"
    spacing: "8dp"
    canvas.before:
        Color:
            rgba: 0.045, 0.06, 0.10, 1
        Rectangle:
            pos: self.pos
            size: self.size

    Label:
        text: "[b]TOFIK AI PHOTO[/b]  [color=55c8ff]V2[/color]"
        markup: True
        font_size: "23sp"
        size_hint_y: None
        height: "44dp"
    Label:
        text: "Offline photo studio • Choose a photo to start"
        font_size: "12sp"
        color: .72, .78, .86, 1
        size_hint_y: None
        height: "22dp"
    Image:
        id: preview
        source: ""
        fit_mode: "contain"
    Label:
        id: status
        text: "No photo selected"
        size_hint_y: None
        height: "38dp"
        color: .9, .94, 1, 1
        halign: "center"
        valign: "middle"
        text_size: self.size
    GridLayout:
        cols: 2
        spacing: "7dp"
        size_hint_y: None
        height: "156dp"
        Button:
            text: "Choose Photo"
            on_release: root.choose_photo()
        Button:
            text: "AI Enhance*"
            on_release: root.apply("enhance")
        Button:
            text: "HD Upscale*"
            on_release: root.apply("upscale")
        Button:
            text: "Face Enhance*"
            on_release: root.apply("face")
        Button:
            text: "Beauty Filter"
            on_release: root.apply("beauty")
        Button:
            text: "Cartoon"
            on_release: root.apply("cartoon")
        Button:
            text: "B&W"
            on_release: root.apply("bw")
        Button:
            text: "Sepia"
            on_release: root.apply("sepia")
        Button:
            text: "Background Remove*"
            on_release: root.advanced_notice("Background removal")
        Button:
            text: "Remove Objects*"
            on_release: root.advanced_notice("Object removal")
        Button:
            text: "Reset"
            on_release: root.reset_photo()
        Button:
            text: "Save Photo"
            on_release: root.save_photo()
    Label:
        text: "* Basic offline approximations where possible; true AI tools need separate model files."
        font_size: "10sp"
        color: .65, .72, .8, 1
        size_hint_y: None
        height: "28dp"
"""


class EditorUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original = None
        self.edited = None

    def set_status(self, msg):
        self.ids.status.text = msg

    def choose_photo(self):
        try:
            filechooser.open_file(
                on_selection=self._selected,
                filters=[("Images", "*.png", "*.jpg", "*.jpeg", "*.webp")]
            )
        except Exception as e:
            self.set_status("Picker error: " + str(e))

    def _selected(self, selection):
        if not selection:
            return
        try:
            img = PILImage.open(selection[0]).convert("RGB")
            # Keep memory use reasonable on phones with 4 GB RAM.
            img.thumbnail((2400, 2400), PILImage.Resampling.LANCZOS)
            self.original = img.copy()
            self.edited = img.copy()
            self.refresh_preview()
            self.set_status("Photo loaded. Select an editing tool.")
        except Exception as e:
            self.set_status("Could not open image: " + str(e))

    def require_photo(self):
        if self.edited is None:
            self.set_status("First choose a photo.")
            return False
        return True

    def apply(self, mode):
        if not self.require_photo():
            return
        img = self.edited.copy()

        if mode == "enhance":
            img = ImageOps.autocontrast(img, cutoff=1)
            img = ImageEnhance.Color(img).enhance(1.10)
            img = ImageEnhance.Contrast(img).enhance(1.10)
            img = ImageEnhance.Sharpness(img).enhance(1.35)
            self.set_status("Enhancement applied (classic image processing, offline).")

        elif mode == "upscale":
            # Enlarges pixels with high-quality interpolation; this is NOT AI super-resolution.
            w, h = img.size
            img = img.resize((min(w * 2, 3200), min(h * 2, 3200)),
                             PILImage.Resampling.LANCZOS)
            img = img.filter(ImageFilter.UnsharpMask(radius=1.4, percent=110, threshold=3))
            self.set_status("2x resize applied. This is not AI detail reconstruction.")

        elif mode == "face":
            # Global portrait-friendly adjustment; no face recognition/model is included.
            img = ImageEnhance.Color(img).enhance(1.06)
            img = ImageEnhance.Brightness(img).enhance(1.025)
            img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=85, threshold=4))
            self.set_status("Portrait tone applied. Dedicated AI face restoration is not included.")

        elif mode == "beauty":
            # Mild smoothing while retaining some edges.
            smooth = img.filter(ImageFilter.GaussianBlur(radius=1.1))
            edges = img.filter(ImageFilter.FIND_EDGES).convert("L")
            edges = ImageOps.invert(edges).point(lambda p: 255 if p > 215 else 0)
            img = PILImage.composite(smooth, img, edges)
            img = ImageEnhance.Brightness(img).enhance(1.02)
            self.set_status("Soft beauty filter applied.")

        elif mode == "cartoon":
            small = img.filter(ImageFilter.MedianFilter(size=5))
            small = ImageOps.posterize(small, bits=4)
            edges = img.convert("L").filter(ImageFilter.FIND_EDGES)
            edges = ImageOps.invert(edges).point(lambda p: 0 if p < 65 else 255)
            img = ImageOps.grayscale(small).convert("RGB")
            img = PILImage.composite(small, img, edges)
            self.set_status("Cartoon effect applied.")

        elif mode == "bw":
            img = ImageOps.grayscale(img).convert("RGB")
            self.set_status("Black and white filter applied.")

        elif mode == "sepia":
            img = ImageOps.colorize(ImageOps.grayscale(img), "#332116", "#f3d7a1").convert("RGB")
            self.set_status("Sepia filter applied.")

        self.edited = img
        self.refresh_preview()

    def advanced_notice(self, feature):
        Popup(
            title=feature,
            content=Label(
                text=(feature + " needs a dedicated AI segmentation/inpainting model. "
                      "This starter build does not pretend to perform that AI task. "
                      "It remains fully offline for the included tools."),
                halign="center"
            ),
            size_hint=(.9, .42)
        ).open()

    def reset_photo(self):
        if self.original is None:
            self.set_status("First choose a photo.")
            return
        self.edited = self.original.copy()
        self.refresh_preview()
        self.set_status("Original image restored.")

    def refresh_preview(self):
        app = App.get_running_app()
        preview_path = os.path.join(app.user_data_dir, "preview.jpg")
        self.edited.save(preview_path, "JPEG", quality=90)
        self.ids.preview.source = preview_path
        self.ids.preview.reload()

    def save_photo(self):
        if not self.require_photo():
            return
        try:
            app = App.get_running_app()
            out_dir = os.path.join(app.user_data_dir, "EditedPhotos")
            os.makedirs(out_dir, exist_ok=True)
            name = "TofikAI_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
            path = os.path.join(out_dir, name)
            self.edited.save(path, "JPEG", quality=95)
            self.set_status("Saved in app storage: " + path)
            Popup(
                title="Saved",
                content=Label(text="Edited photo saved in the app's private storage."),
                size_hint=(.82, .3)
            ).open()
        except Exception as e:
            self.set_status("Save error: " + str(e))


class TofikAIPhotoApp(App):
    def build(self):
        self.title = "Tofik AI Photo"
        Builder.load_string(KV)
        return EditorUI()


if __name__ == "__main__":
    TofikAIPhotoApp().run()
