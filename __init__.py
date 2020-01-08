# Copyright 2014-2020 Ahmet Cetinkaya

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

class PasteFromHTMLMainWindowExtension(MainWindowExtension):
    uimanager_xml = '''
    <ui>
    <menubar name='menubar'>
    <menu action='tools_menu'>
    <placeholder name='plugin_items'>
    <menuitem action='pastefh'/>
    </placeholder>
    </menu>
    </menubar>
    </ui>
    '''

    def get_clipboard_target_and_data(self):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        result, targets = clipboard.wait_for_targets()
        if not result:
                return None
        my_target_strings = ["text/html", "TEXT/HTML", "utf8-string", "UTF8-STRING",
                             "text", "TEXT", "string", "STRING"]
        target_strings = [atom.name() for atom in targets]
        for my_target_string in my_target_strings:
            if my_target_string in target_strings:
                data = clipboard.wait_for_contents(Gdk.Atom.intern(my_target_string, False)).get_data()
                if b'\xff' in data:
                    return (my_target_string, data.decode('utf_16').replace('\x00', ''))
                elif b'\x00' in data:
                    return (my_target_string, data.decode('utf_8').replace('\x00', ''))
                return (my_target_string, data.decode('utf_8'))
        return None

    @action(_('_Paste from HTML'), accelerator="<ctrl><shift>v")
    def pastefh(self):
        buffer = self.window.pageview.textview.get_buffer()
        h = HTMLCDParser()
        target_and_data = self.get_clipboard_target_and_data()
        if target_and_data is not None:
            target = target_and_data[0]
            data = target_and_data[1]
            if target in ["text/html", "TEXT/HTML"]:
                buffer.insert_at_cursor(data + "\n\n")
                buffer.insert_at_cursor(h.to_zim(data))
            else:
                buffer.insert_at_cursor(data)
