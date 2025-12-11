import gi
import base64
import os

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

class ContactApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.example.ContactApp")

    def do_activate(self):
        window = Gtk.ApplicationWindow(application=self)
        window.set_title("Créateur de vCard")
        window.set_default_size(400, 400)

        grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        grid.set_margin_top(20)
        grid.set_margin_bottom(20)
        grid.set_margin_start(20)
        grid.set_margin_end(20)
        window.set_child(grid)

        # Choix du thème
        self.theme_combo = Gtk.ComboBoxText()
        for theme in ["famille", "amis", "pro", "divers"]:
            self.theme_combo.append_text(theme)
        self.theme_combo.set_active(0)
        grid.attach(Gtk.Label(label="Thème :"), 0, 0, 1, 1)
        grid.attach(self.theme_combo, 1, 0, 1, 1)

        # Champs texte
        self.name_entry = Gtk.Entry(placeholder_text="Nom complet")
        self.email_entry = Gtk.Entry(placeholder_text="Email")
        self.phone_entry = Gtk.Entry(placeholder_text="Téléphone")

        grid.attach(Gtk.Label(label="Nom :"), 0, 1, 1, 1)
        grid.attach(self.name_entry, 1, 1, 1, 1)
        grid.attach(Gtk.Label(label="Email :"), 0, 2, 1, 1)
        grid.attach(self.email_entry, 1, 2, 1, 1)
        grid.attach(Gtk.Label(label="Téléphone :"), 0, 3, 1, 1)
        grid.attach(self.phone_entry, 1, 3, 1, 1)

        # Widget image + bouton pour charger
        self.image = Gtk.Image()
        grid.attach(Gtk.Label(label="Photo :"), 0, 4, 1, 1)
        grid.attach(self.image, 1, 4, 1, 1)

        button_photo = Gtk.Button(label="Choisir une photo")
        button_photo.connect("clicked", self.on_choose_photo)
        grid.attach(button_photo, 0, 5, 2, 1)

        # Bouton Exporter
        button_export = Gtk.Button(label="Exporter en vCard")
        button_export.connect("clicked", self.on_export_clicked)
        grid.attach(button_export, 0, 6, 2, 1)

        # Variable pour stocker le chemin de la photo
        self.photo_path = None

        window.present()

    def on_choose_photo(self, button):
        dialog = Gtk.FileChooserNative(
            title="Choisir une photo",
            transient_for=button.get_root(),
            action=Gtk.FileChooserAction.OPEN,
            accept_label="Ouvrir",
            cancel_label="Annuler"
        )

        filter_img = Gtk.FileFilter()
        filter_img.add_mime_type("image/jpeg")
        filter_img.add_mime_type("image/png")
        dialog.add_filter(filter_img)

        dialog.connect("response", self.on_file_response)
        dialog.show()

    def on_file_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            if file:
                self.photo_path = file.get_path()
                self.image.set_from_file(self.photo_path)
        dialog.destroy()

    def on_export_clicked(self, button):
        theme = self.theme_combo.get_active_text()
        config_dir = os.path.expanduser("~/.config/contacts")
        os.makedirs(config_dir, exist_ok=True)
        filepath = os.path.join(config_dir, f"{theme}.vcard")
        self.save_vcard(filepath)

    def save_vcard(self, filepath):
        name = self.name_entry.get_text()
        email = self.email_entry.get_text()
        phone = self.phone_entry.get_text()

        vcard = f"""BEGIN:VCARD
VERSION:3.0
FN:{name}
EMAIL:{email}
TEL;TYPE=cell:{phone}
TEL;TYPE=home:+33 4 00 00 00 00
"""

        if self.photo_path:
            with open(self.photo_path, "rb") as img_file:
                b64_photo = base64.b64encode(img_file.read()).decode("utf-8")
                vcard += f"PHOTO;ENCODING=b;TYPE=JPEG:{b64_photo}\n"

        vcard += "END:VCARD\n"

        with open(filepath, "a", encoding="utf-8") as f:  # append
            f.write(vcard)

        print(f"Fichier vCard ajouté dans : {filepath}") 

        self.quit()  

if __name__ == "__main__":
    app = ContactApp()
    app.run()
