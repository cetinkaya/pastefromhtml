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

from HTMLParser import HTMLParser
import re

def assoc(key, pairs):
    value = None
    for (k, v) in pairs:
        if k == key:
            value = v
            break
    return value

# HTML Clipboard Data Parser
class HTMLCDParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self) # super().__init__() for Pyhon 3
        self.zim_str = ""
        self.beg = {"h1": "== ",
                    "h2": "=== ",
                    "h3": "==== ",
                    "h4": "===== ",
                    "h5": "====== ",
                    "h6": "====== ",
                    "strong": "**",
                    "b": "**",
                    "i": "//",
                    "em": "//",
                    "u": "__",
                    "ins": "__",
                    "mark": "__",
                    "pre": "''",
                    "strike": "~~",
                    "p": "",
                    "div": "",
                    "ol": "",
                    "ul": "",
                    "li": ""}

        self.end = {"h1": " ==",
                    "h2": " ===",
                    "h3": " ====",
                    "h4": " =====",
                    "h5": " ======",
                    "h6": " ======",
                    "strong": "**",
                    "b": "**",
                    "i": "//",
                    "em": "//",
                    "u": "__",
                    "ins": "__",
                    "mark": "__",
                    "pre": "''",
                    "strike": "~~",
                    "p": "\n",
                    "div": "\n",
                    "a": "]]",
                    "ol": "\n",
                    "ul": "\n",
                    "li": "\n"}
        self.list_type = "ol"
        self.item_no = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.beg.keys():
            self.zim_str += self.beg[tag]
        if tag == "a":
            href = assoc("href", attrs)
            if href is None:
                href = "#"
            self.zim_str += "[[{}|".format(href)
        elif tag == "ol":
            self.list_type = "ol"
            self.item_no = 0
        elif tag == "ul":
            self.list_type = "ul"
            self.item_no = 0
        elif tag == "li":
            self.item_no += 1
            if self.list_type == "ol":
                self.zim_str += "{}. ".format(self.item_no)
            else:
                self.zim_str += "* "
        elif tag == "img":
            src = assoc("src", attrs)
            if src is None:
                src = "#"
            alt = assoc("alt", attrs)
            if alt is None:
                alt = "Image"
            self.zim_str += "[[{0}|{1}]]".format(src, alt)


    def handle_endtag(self, tag):
        if tag in self.end.keys():
            self.zim_str += self.end[tag]

    def handle_data(self, data):
        space_removed_data = data # re.sub(r"[\s]+", " ", data)
        self.zim_str += space_removed_data

    def handle_startendtag(self, tag, attrs):
        if tag == "br":
            self.zim_str += "\n\n"
        elif tag == "input":
            if assoc("type", attrs) in ["checkbox", "radio"]:
                is_checked = assoc("checked", attrs)
                if not (is_checked is None) and is_checked.lower() == "true":
                    self.zim_str += "[*] "
                else:
                    self.zim_str += "[ ] "
        elif tag == "img":
            src = assoc("src", attrs)
            if src is None:
                src = "#"
            alt = assoc("alt", attrs)
            if alt is None:
                alt = "Image"
            self.zim_str += "[[{0}|{1}]]".format(src, alt)
            
    def to_zim(self, html_str):
        self.feed(html_str)
        return re.sub(r'\n+', "\n", self.zim_str).strip("\n")
