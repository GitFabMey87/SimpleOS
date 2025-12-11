#!/bin/bash

# Crée une archive du dossier $HOME/.config/contacts
ARCHIVE="$HOME/contacts.tar.gz"
tar -czf "$ARCHIVE" -C "$HOME/.config" contacts

# Vérifie si la commande tar a réussi
if [ $? -eq 0 ]; then
    # Affiche une fenêtre de confirmation avec Zenity
    zenity --question \
      --title="Export terminé" \
      --text="Le fichier a été exporté dans :\n$ARCHIVE\n\nVoulez-vous ouvrir Thunar à cet endroit ?" \
      --ok-label="Ouvrir Thunar" \
      --cancel-label="Fermer"

    # Si l’utilisateur clique sur "Ouvrir Thunar"
    if [ $? -eq 0 ]; then
        thunar "$(dirname "$ARCHIVE")"
    fi
else
    # Si la compression échoue, affiche une erreur
    zenity --error \
      --title="Erreur" \
      --text="L'export a échoué. Vérifiez le dossier $HOME/.config/contacts."
fi
