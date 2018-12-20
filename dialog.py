#!/usr/bin/python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def on_info(window, primary, secondary):
    dialog = Gtk.MessageDialog(window, 0, Gtk.MessageType.INFO,
        Gtk.ButtonsType.OK, primary)
    dialog.format_secondary_text(secondary)
    dialog.run()
    print("INFO dialog closed")

    dialog.destroy()

def on_error(window, primary, secondary):
    dialog = Gtk.MessageDialog(window, 0, Gtk.MessageType.ERROR,
        Gtk.ButtonsType.CANCEL, primary)
    dialog.format_secondary_text(secondary)
    dialog.run()
    print("ERROR dialog closed")

    dialog.destroy()

def on_warn(window, primary, secondary):
    dialog = Gtk.MessageDialog(window, 0, Gtk.MessageType.WARNING,
        Gtk.ButtonsType.OK, primary)
    dialog.format_secondary_text(secondary)
    response = dialog.run()
    if response == Gtk.ResponseType.OK:
        print("WARN dialog closed by clicking OK button")

    dialog.destroy()

def on_question(window, primary, secondary):
    dialog = Gtk.MessageDialog(window, 0, Gtk.MessageType.QUESTION,
        Gtk.ButtonsType.YES_NO, primary)
    dialog.format_secondary_text(secondary)
    response = dialog.run()
    if response == Gtk.ResponseType.YES:
        print("QUESTION dialog closed by clicking YES button")
        dialog.destroy()
        return True
    elif response == Gtk.ResponseType.NO:
        print("QUESTION dialog closed by clicking NO button")
        dialog.destroy()
        return False
