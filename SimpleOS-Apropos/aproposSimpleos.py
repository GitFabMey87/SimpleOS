#!/usr/bin/env python3
import gi, subprocess
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

class AboutWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Simple.os")
        self.set_default_size(500, 400)
        self.set_icon_name("contacts")

        # Conteneur vertical
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        vbox.set_margin_top(20)
        vbox.set_margin_bottom(20)
        vbox.set_margin_start(20)
        vbox.set_margin_end(20)
        self.set_child(vbox)

        # Texte d'introduction
        label = Gtk.Label(label="Bienvenue dans Simple.os\n"
                                "Une distribution légère et personnalisée basée sur Debian et XFCE.\n\n" "Initié par fabrice Meynard un soir de septembre 2025\n\n")
        label.set_wrap(True)
        label.set_halign(Gtk.Align.CENTER)
        vbox.append(label)

        # Première ligne centrée
        hbox1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        hbox1.set_halign(Gtk.Align.CENTER)
        vbox.append(hbox1)

        icon1 = Gtk.Image.new_from_file("/usr/share/icons/SimpleOS-icons/scalable/apps/SLogo.svg")
        button1 = Gtk.Button()
        button1.set_child(icon1)
        button1.connect("clicked", lambda x: self.open_url("https://simpleos.org"))
        hbox1.append(button1)

        icon2 = Gtk.Image.new_from_file("/usr/share/icons/SimpleOS-icons/scalable/apps/SLogo.svg")
        button2 = Gtk.Button()
        button2.set_child(icon2)
        button2.connect("clicked", lambda x: self.open_url("https://github.com/simpleos"))
        hbox1.append(button2)

        # Deuxième ligne centrée
        hbox2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        hbox2.set_halign(Gtk.Align.CENTER)
        vbox.append(hbox2)

        icon3 = Gtk.Image.new_from_file("/usr/share/icons/SimpleOS-icons/scalable/apps/SLogo.svg")
        button3 = Gtk.Button()
        button3.set_child(icon3)
        button3.connect("clicked", lambda x: self.open_url("https://brave.com"))
        hbox2.append(button3)

        icon4 = Gtk.Image.new_from_file("/usr/share/icons/SimpleOS-icons/scalable/apps/SLogo.svg")
        button4 = Gtk.Button()
        button4.set_child(icon4)
        button4.connect("clicked", lambda x: self.open_url("https://debian.org"))
        hbox2.append(button4)

        # Bouton Quitter centré
        quit_button = Gtk.Button(label="Quitter")
        quit_button.connect("clicked", lambda x: self.close())
        quit_button.set_halign(Gtk.Align.CENTER)
        vbox.append(quit_button)

    def open_url(self, url):
        subprocess.Popen(["brave-browser", url])

class AboutApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.madistri.about")

    def do_activate(self):
        win = AboutWindow(self)
        win.present()

if __name__ == "__main__":
    app = AboutApp()
    app.run()