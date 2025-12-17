#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('GdkX11', '4.0')  # Pour vérifier X11
from gi.repository import Gtk, GLib, Gdk, GdkX11
import datetime
import os
import Xlib
from Xlib.display import Display
from Xlib import X
import psutil  # Assurez-vous d'installer psutil : sudo apt install python3-psutil ou pip install psutil
import subprocess

# Hauteur de la barre
BAR_HEIGHT = 30

# Fonction pour mettre à jour l'horloge
def update_clock(label):
    now = datetime.datetime.now()
    label.set_label(now.strftime("%H:%M:%S"))
    return True

# Fonction pour mettre à jour l'indicateur de batterie
def update_battery(battery_label):
    battery = psutil.sensors_battery()
    if battery:
        percent = battery.percent
        plugged = " (branchée)" if battery.power_plugged else ""
        battery_label.set_label(f"Batterie: {percent}%{plugged}")
    else:
        battery_label.set_label("Batterie: N/A")
    return True

# Fonction pour mettre à jour l'indicateur de réseau
def update_network(network_label):
    net_stats = psutil.net_if_stats()
    connected = any(stats.isup for stats in net_stats.values() if stats.isup)
    status = "Connecté" if connected else "Déconnecté"
    network_label.set_label(f"Réseau: {status}")
    return True

# Fonction pour rafraîchir la liste des fenêtres avec wmctrl
def refresh_window_list(popover_box):
    # Vider la box
    child = popover_box.get_first_child()
    while child:
        popover_box.remove(child)
        child = popover_box.get_first_child()

    # Obtenir la liste des fenêtres via wmctrl -l
    try:
        output = subprocess.check_output(["wmctrl", "-l"]).decode("utf-8")
        lines = output.strip().split("\n")
        for line in lines:
            parts = line.split(None, 3)  # Split sur les 4 premiers champs (id, desktop, geometry, title)
            if len(parts) < 4:
                continue
            window_id = parts[0]
            title = parts[3]  # Le titre
            button = Gtk.Button(label=title[:50])  # Tronquer si trop long
            button.connect("clicked", lambda b, wid=window_id: os.system(f"wmctrl -i -a {wid}"))
            popover_box.append(button)
    except FileNotFoundError:
        error_label = Gtk.Label(label="wmctrl non installé (sudo apt install wmctrl)")
        popover_box.append(error_label)
    except Exception as e:
        error_label = Gtk.Label(label=f"Erreur: {e}")
        popover_box.append(error_label)

# Créer la fenêtre principale (barre)
window = Gtk.Window()
window.set_decorated(False)  # Pas de bordures
window.set_name("custom-panel")

# Style CSS pour la barre (fond noir, texte blanc)
css = """
#custom-panel {
    background-color: #333333;
    color: white;
    font-size: 14px;
}
button {
    background: transparent;
    border: none;
}
"""
style_provider = Gtk.CssProvider()
style_provider.load_from_data(bytes(css.encode()))
Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

# Utiliser Gtk.CenterBox pour centrer les éléments
center_box = Gtk.CenterBox()
window.set_child(center_box)

# Partie gauche : Outils divers (exemples)
left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
left_box.set_margin_start(10)
center_box.set_start_widget(left_box)

# Exemple : Label utilisateur
user_label = Gtk.Label(label=os.getlogin())
left_box.append(user_label)

# Exemple : Bouton pour ouvrir un terminal
term_button = Gtk.Button(label="Terminal")
term_button.connect("clicked", lambda _: os.system("x-terminal-emulator &"))
left_box.append(term_button)

# Indicateur de batterie
battery_label = Gtk.Label(label="Batterie: N/A")
left_box.append(battery_label)
GLib.timeout_add(30000, update_battery, battery_label)  # Mise à jour toutes les 30 secondes

# Indicateur de réseau
network_label = Gtk.Label(label="Réseau: N/A")
left_box.append(network_label)
GLib.timeout_add(10000, update_network, network_label)  # Mise à jour toutes les 10 secondes

# Bouton pour la liste des fenêtres ouvertes
windows_button = Gtk.MenuButton()
windows_button.set_icon_name("view-list-symbolic")  # Icône exemple

windows_popover = Gtk.Popover()
windows_popover_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
windows_popover_box.set_margin_start(5)
windows_popover_box.set_margin_end(5)
windows_popover_box.set_margin_top(5)
windows_popover_box.set_margin_bottom(5)
windows_popover.set_child(windows_popover_box)
windows_button.set_popover(windows_popover)

# Rafraîchir la liste quand le popover s'affiche
def on_popover_show(popover, box):
    refresh_window_list(box)
windows_popover.connect("show", on_popover_show, windows_popover_box)

left_box.append(windows_button)

# Ajoutez d'autres outils ici (ex: indicateur CPU avec psutil, etc.)

# Centre : Horloge
clock_label = Gtk.Label(label="00:00:00")
clock_label.set_margin_start(10)
clock_label.set_margin_end(10)
center_box.set_center_widget(clock_label)
GLib.timeout_add(1000, update_clock, clock_label)  # Mise à jour chaque seconde

# Partie droite : 6 icônes avec menus déroulants
right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
right_box.set_margin_end(10)
center_box.set_end_widget(right_box)

icons = ["applications-system-symbolic", "folder-symbolic", "mail-send-symbolic", "preferences-system-symbolic", "system-shutdown-symbolic", "help-browser-symbolic"]
for icon_name in icons:
    menu_button = Gtk.MenuButton()
    menu_button.set_icon_name(icon_name)

    # Créer un popover avec 4 options (exemples de boutons)
    popover = Gtk.Popover()
    popover_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    popover_box.set_margin_start(5)
    popover_box.set_margin_end(5)
    popover_box.set_margin_top(5)
    popover_box.set_margin_bottom(5)
    for i in range(4):
        option_button = Gtk.Button(label=f"Option {i+1}")
        # Personnalisez : Connectez à une action, ex: option_button.connect("clicked", lambda _, cmd="echo 'Option {i+1}'": os.system(cmd))
        popover_box.append(option_button)
    popover.set_child(popover_box)
    menu_button.set_popover(popover)

    right_box.append(menu_button)

# Obtenir les infos sur l'écran et les moniteurs
display = Gdk.Display.get_default()
monitors = display.get_monitors()
if not monitors:
    print("Aucun moniteur détecté.")
    exit(1)

# Utiliser le premier moniteur (adaptez pour multi-écrans si besoin)
primary_monitor = monitors[0]
geom = primary_monitor.get_geometry()
screen_width = geom.width
screen_x = geom.x  # Offset pour multi-moniteurs

# Calculer la largeur : 2/3 de l'écran
panel_width = (2 * screen_width) // 3

# Définir la taille
window.set_size_request(panel_width, BAR_HEIGHT)

# Afficher la fenêtre d'abord (présente et mappe)
window.present()

# Maintenant, configurer via Xlib (après present pour que la position soit respectée)
surface = window.get_surface()
try:
    if not isinstance(surface, GdkX11.X11Surface):
        raise Exception("Non-X11 backend (probablement Wayland) ; hints non supportés.")

    xdisplay = Display()
    xwindow = xdisplay.create_resource_object('window', surface.get_xid())

    # Positionner la fenêtre via Xlib : centrée en haut
    panel_x = screen_x + (screen_width - panel_width) // 2
    xwindow.configure(x=panel_x, y=0)

    # Définir le type de fenêtre comme DOCK
    atom_window_type = xdisplay.intern_atom('_NET_WM_WINDOW_TYPE')
    atom_dock = xdisplay.intern_atom('_NET_WM_WINDOW_TYPE_DOCK')
    xwindow.change_property(atom_window_type, X.atom.ATOM, 32, [atom_dock], X.PropModeReplace)

    # Définir l'état ABOVE (toujours au-dessus)
    atom_state = xdisplay.intern_atom('_NET_WM_STATE')
    atom_above = xdisplay.intern_atom('_NET_WM_STATE_ABOVE')
    xwindow.change_property(atom_state, X.atom.ATOM, 32, [atom_above], X.PropModeReplace)

    # _NET_WM_STRUT_PARTIAL : Réserve l'espace seulement pour la zone du panel (top_start_x et top_end_x ajustés)
    strut_partial = [0, 0, BAR_HEIGHT, 0, 0, 0, 0, 0, panel_x, panel_x + panel_width - 1, 0, 0]
    xwindow.change_property(xdisplay.intern_atom('_NET_WM_STRUT_PARTIAL'), xdisplay.intern_atom('CARDINAL'), 32, strut_partial, X.PropModeReplace)

    # _NET_WM_STRUT (pour compatibilité, ajusté pareil)
    strut = [0, 0, BAR_HEIGHT, 0]
    xwindow.change_property(xdisplay.intern_atom('_NET_WM_STRUT'), xdisplay.intern_atom('CARDINAL'), 32, strut, X.PropModeReplace)

    xdisplay.sync()
except ImportError:
    print("python-xlib non installé ; la barre pourrait être couverte par d'autres fenêtres.")
except Exception as e:
    print(f"Erreur lors de la configuration X11 : {e}")

# Lancer la boucle principale explicitement
GLib.MainLoop().run()