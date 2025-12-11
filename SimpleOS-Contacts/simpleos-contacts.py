import gi, os, base64, subprocess
gi.require_version("Gtk", "4.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import Gtk, GdkPixbuf

class ContactListApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.example.ContactListApp")

    def do_activate(self):
        window = Gtk.ApplicationWindow(application=self)
        window.set_title("")
        window.set_default_size(350, 850)
        window.set_icon_name("contacts")


        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        window.set_child(scrolled)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        scrolled.set_child(self.vbox)

        # Ligne horizontale centrée : combo + boutons
        top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        top_row.set_margin_top(20)
        top_row.set_halign(Gtk.Align.CENTER)

        self.theme_combo = Gtk.ComboBoxText()
        for theme in ["famille", "amis", "pro", "divers"]:
            self.theme_combo.append_text(theme)
        self.theme_combo.set_active(0)
        self.theme_combo.connect("changed", self.load_contacts)
        top_row.append(self.theme_combo)

        plus_icon = Gtk.Image.new_from_file("/usr/share/icons/SimpleOS-icons/scalable/apps/add.svg")
        plus_btn = Gtk.Button()
        plus_btn.set_child(plus_icon)
        plus_btn.set_tooltip_text("Créer un nouveau contact")
        plus_btn.connect("clicked", self.create_vcard)
        top_row.append(plus_btn)

        export_icon = Gtk.Image.new_from_file("/usr/share/icons/SimpleOS-icons/scalable/apps/utilities-terminal.svg")
        export_btn = Gtk.Button()
        export_btn.set_child(export_icon)
        export_btn.set_tooltip_text("Exporter les vCards")
        export_btn.connect("clicked", self.export_vcards)
        top_row.append(export_btn)

        import_icon = Gtk.Image.new_from_file("/usr/share/icons/SimpleOS-icons/scalable/apps/office-word.svg")
        import_btn = Gtk.Button()
        import_btn.set_child(import_icon)
        import_btn.set_tooltip_text("Importer une vCard")
        import_btn.connect("clicked", self.import_vcard)
        top_row.append(import_btn)

        self.vbox.append(top_row)

        # Liste des contacts
        self.list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        self.vbox.append(self.list_box)

        window.present()
        self.load_contacts()

    def clear_box(self, box):
        child = box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            box.remove(child)
            child = next_child

    def load_contacts(self, combo=None):
        self.clear_box(self.list_box)

        theme = self.theme_combo.get_active_text()
        filepath = os.path.expanduser(f"~/.config/contacts/{theme}.vcard")
        if not os.path.exists(filepath):
            return

        with open(filepath, "r", encoding="utf-8") as f:
            data = f.read()

        vcards = data.strip().split("END:VCARD")
        for v in vcards:
            if not v.strip():
                continue
            name, photo_data, email = "", None, None
            for line in v.splitlines():
                if line.startswith("FN:"):
                    name = line[3:]
                if line.startswith("PHOTO;ENCODING=b"):
                    photo_data = line.split(":",1)[1]
                if line.startswith("EMAIL:"):
                    email = line.split(":",1)[1]

            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=30)

            picture = None
            if photo_data:
                try:
                    raw = base64.b64decode(photo_data)
                    loader = GdkPixbuf.PixbufLoader.new()
                    loader.write(raw)
                    loader.close()
                    pixbuf = loader.get_pixbuf()
                    if pixbuf is not None:
                        pixbuf_big = pixbuf.scale_simple(512, 512, GdkPixbuf.InterpType.BILINEAR)
                        picture = Gtk.Picture.new_for_pixbuf(pixbuf_big)
                except Exception:
                    picture = None
            if picture is None:
                fallback = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 512, 512)
                fallback.fill(0xDDDDDDFF)
                picture = Gtk.Picture.new_for_pixbuf(fallback)

            hbox.append(picture)

            vbox_right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            label = Gtk.Label(label=name)
            label.set_xalign(0)
            label.set_css_classes(["title-1"])
            vbox_right.append(label)

            icon_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)

            mail_icon = Gtk.Image.new_from_file("/usr/share/icons/SimpleOS-icons/scalable/apps/internet-mail.svg")
            mail_btn = Gtk.Button()
            mail_btn.set_child(mail_icon)
            mail_btn.set_tooltip_text("Envoyer un mail")
            if email:
                mail_btn.connect("clicked", self.launch_geary, email)
            icon_row.append(mail_btn)

            sms_icon = Gtk.Image.new_from_file("/usr/share/icons/SimpleOS-icons/scalable/apps/contacts.svg")
            sms_btn = Gtk.Button()
            sms_btn.set_child(sms_icon)
            sms_btn.set_tooltip_text("Envoyer un SMS")
            icon_row.append(sms_btn)

            other_icon = Gtk.Image.new_from_file("/usr/share/icons/SimpleOS-icons/scalable/apps/system-file-manager.svg")
            other_btn = Gtk.Button()
            other_btn.set_child(other_icon)
            other_btn.set_tooltip_text("Autre action")
            icon_row.append(other_btn)

            vbox_right.append(icon_row)
            hbox.append(vbox_right)

            self.list_box.append(hbox)

    def launch_geary(self, button, email):
        subprocess.Popen(["geary", f"mailto:{email}"])

    def create_vcard(self, button):
        subprocess.Popen(["python3", "/home/fabrice/Bureau/vcards/simpleos-nouveaucontact.py"])
        self.quit() 

    def export_vcards(self, button):
        subprocess.Popen(["/home/fabrice/Bureau/vcards/simpleos-export-contacts.sh"])

    def import_vcard(self, button):
        subprocess.Popen(["/home/fabrice/Bureau/vcards/simpleos-import-contacts.sh"])

if __name__ == "__main__":
    app = ContactListApp()
    app.run()