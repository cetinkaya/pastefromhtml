# Copyright 2014-2022 Ahmet Cetinkaya

# This file is part of pastefromhtml.
# pastefromhtml is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# pastefromhtml is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with pastefromhtml. If not, see <http://www.gnu.org/licenses/>.

from zim.plugins import PluginClass
from zim.gui.mainwindow import MainWindowExtension
from zim.actions import action

from gi.repository import Gdk, Gtk
from .htmlcdparser import HTMLCDParser


class PasteFromHTMLPlugin(PluginClass):
    plugin_info = {
        "name": _("Paste from HTML"),
        "description": _("This plugin lets you paste HTML clipboard data."),
        "author": "Ahmet Cetinkaya",
        "help": "Plugins:Paste from HTML"
    }

    plugin_preferences = (
        # key, type, label, default
        ('image_inside_a', 'bool', _('For image tags <img> inside anchor tags <a>, paste images instead of links'), False),
        ('reload_page', 'bool', _('Reload page after pasting'), False),
    )


def get_fragment(data):
    start_tag = '<!--StartFragment-->'
    end_tag = '<!--EndFragment-->'
    start_tag_index = data.find(start_tag)
    end_tag_index = data.find(end_tag)

    clip_start = 0
    clip_end = len(data)
    if start_tag_index >= 0:
        clip_start = start_tag_index + len(start_tag)
    if end_tag_index >= 0:
        clip_end = end_tag_index

    return data[clip_start:clip_end]


def get_clipboard_target_and_data():
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    result, targets = clipboard.wait_for_targets()
    if not result:
        return None
    my_target_strings = ["text/html", "TEXT/HTML", "utf8-string", "UTF8-STRING",
                         "text", "TEXT", "string", "STRING", "HTML Format", "UTF8_STRING"]
    target_strings = [atom.name() for atom in targets]
    for my_target_string in my_target_strings:
        if my_target_string in target_strings:
            data = clipboard.wait_for_contents(Gdk.Atom.intern(my_target_string, False)).get_data()
            if b'\xff' in data:
                return my_target_string, data.decode('utf_16').replace('\x00', '')
            elif b'\x00' in data:
                return my_target_string, data.decode('utf_8').replace('\x00', '')
            return my_target_string, data.decode('utf_8')
    return None


class PasteFromHTMLMainWindowExtension(MainWindowExtension):

    def __init__(self, plugin, window):
        MainWindowExtension.__init__(self, plugin, window)
        self.plugin = plugin
        self.on_preferences_changed(self.plugin.preferences)
        self.plugin.preferences.connect('changed', self.on_preferences_changed)
        self.window.pageview.textview.connect("populate-popup", self.on_populate_popup)

    def on_preferences_changed(self, preferences):
        self.preferences = preferences

    @action(_('_Paste from HTML'), accelerator="<ctrl><shift>v", menuhints='tools')
    def pastefh(self):
        folder = self.window.notebook.get_attachments_dir(self.window.pageview.page)
        buffer = self.window.pageview.textview.get_buffer()
        target_and_data = get_clipboard_target_and_data()

        if target_and_data is not None:
            target = target_and_data[0]
            data = target_and_data[1]

            if target in ["text/html", "TEXT/HTML", "HTML Format"]:
                data = get_fragment(data)
                cursor = self.window.pageview.get_cursor_pos()
                h = HTMLCDParser(self.preferences['image_inside_a'])
                buffer.insert_at_cursor(h.to_zim(data, folder))
                self.window.pageview.set_page(self.window.pageview.page)
                self.window.pageview.set_cursor_pos(cursor)
            else:
                buffer.insert_at_cursor(data)
            if self.preferences['reload_page']:
                self.window.pageview.reload_page()

    @action(_('_Paste from HTML'), accelerator="<ctrl><shift>v", menuhints='edit')
    def pastefh_edit(self):
        self.pastefh()

    def on_populate_popup(self, view, menu):
        menu.append(Gtk.SeparatorMenuItem())
        item = Gtk.MenuItem.new_with_mnemonic(_('_Paste from HTML'))
        item.connect('activate', lambda o: self.pastefh())
        menu.append(item)
        menu.show_all()
