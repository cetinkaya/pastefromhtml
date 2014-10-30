# Copyright 2014 Ahmet Cetinkaya

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

from zim.plugins import PluginClass, extends, WindowExtension
from zim.actions import action

import gtk
import htmlcdparser as hcdp

class PasteFromHTMLPlugin(PluginClass):
    plugin_info = {
        "name": _("Paste from HTML"),
        "description": _("This plugin lets you paste HTML clipboard data."),
        "author": "Ahmet Cetinkaya",
        "help": "Plugins:Paste from HTML"
    }
    
@extends('MainWindow')
class MainWindowExtension(WindowExtension):
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

    def get_clipboard_data(self):
        my_targets = ["text/html", "TEXT/HTML", "utf8-string", "UTF8-STRING",
                      "text", "TEXT", "string", "STRING"]
        clipboard = gtk.Clipboard()
        targets = clipboard.wait_for_targets()
        data = ""
        for my_target in my_targets:
            if my_target in targets:
                data = clipboard.wait_for_contents(my_target).data
                data = data.replace(b"\x00", b"").replace(b"\xff", b"").replace(b"\xfe", b"").decode("utf-8")
                return data

        return data
    
    @action(_('_Paste from HTML'), accelerator="<ctrl><shift>v")
    def pastefh(self):
        buffer = self.window.pageview.view.get_buffer()
        h = hcdp.HTMLCDParser()
        buffer.insert_at_cursor(h.to_zim(self.get_clipboard_data()))
