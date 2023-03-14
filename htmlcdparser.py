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

from html.parser import HTMLParser
from html.entities import name2codepoint
import re
import urllib.request, urllib.error, urllib.parse
import os

def assoc(key, pairs):
    value = None
    for (k, v) in pairs:
        if k == key:
            value = v
            break
    return value

#download file of url
def get_url(url, name):
    f = open(name,'wb')
    req = urllib.request.Request(url)
    req.add_unredirected_header('User-agent', 'Mozilla')
    f.write(urllib.request.urlopen(req).read())
    f.close()

# HTML Clipboard Data Parser
class HTMLCDParser(HTMLParser):
    def __init__(self, image_inside_a):
        HTMLParser.__init__(self) # super().__init__() for Pyhon 3
        self.image_inside_a = image_inside_a
        self.zim_str = ""
        self.beg = {"h1": "====== ",
                    "h2": "===== ",
                    "h3": "==== ",
                    "h4": "=== ",
                    "h5": "== ",
                    "iframe": "[[",
                    "strong": "**",
                    "b": "**",
                    "i": "//",
                    "em": "//",
                    "u": "__",
                    "ins": "__",
                    "mark": "__",
                    "pre": "''",
                    "code": "''",
                    "blockquote": "",
                    "strike": "~~",
                    "del": "~~",
                    "p": "",
                    "div": "",
                    "ol": "",
                    "ul": "",
                    "dl": "",
                    "dt": "",
                    "dd": "\t",
                    "li": "",
                    "table": "",
                    "caption": "",
                    "tr": "",
                    "th": "|",
                    "td": "|",
                    "hr": "-----\n",
                    "sup": "^{",
                    "sub": "_{",
                    "span": "",
                    "figure": "",
                    "figcaption": "\n",
                    "abbr": "",
                    "q": "",
                    "time": ""}
        self.end = {"h1": " ======\n",
                    "h2": " =====\n",
                    "h3": " ====\n",
                    "h4": " ===\n",
                    "h5": " ==\n",
                    "iframe": "]]",
                    "strong": "**",
                    "b": "**",
                    "i": "//",
                    "em": "//",
                    "u": "__",
                    "ins": "__",
                    "mark": "__",
                    "pre": "''",
                    "code": "''",
                    "blockquote": "",
                    "strike": "~~",
                    "del": "~~",
                    "p": "\n",
                    "div": "\n",
                    "a": "]]",
                    "ol": "\n",
                    "ul": "\n",
                    "dl": "\n",
                    "dt": ":\n",
                    "dd": "\n",
                    "li": "",
                    "table": "\n",
                    "caption": "\n",
                    "tr": "|\n",
                    "th": "",
                    "td": "",
                    "sup": "}",
                    "sub": "}",
                    "figure": "\n",
                    "figcaption": "\n"}
        self.list_type = "ol"
        self.item_no = 0
        self.inside_p = False
        self.inside_pre = False
        self.pre_data = ""
        self.inside_blockquote = False
        self.inside_tag = "" #Indicate label on which we are
        self.start_tag = "" #Initial tag in case we have to delete it
        self.del_tag = ""
        self.tag_attrib = "" #Tag Attribute Value
        self.folder = None
        self.a_href = "" #Link of a tag
        self.inside_li = False
        self.list_level = -1
        self.inside_iframe = False
        self.inside_span = False
        self.inside_dl = False
        self.inside_table = False

    def handle_starttag(self, tag, attrs):
        #If we are in a non-nestable tag we do nothing
        if self.inside_tag and not (self.inside_tag == "a" and tag == "img" and self.a_href) and not(self.inside_tag == "th" or self.inside_tag == "td" or self.inside_tag == "dt" or self.inside_tag == "dd") and not (tag == "a" and (self.inside_tag == "b" or self.inside_tag == "strong" or self.inside_tag == "i" or self.inside_tag == "em" or self.inside_tag == "u" or self.inside_tag == "ins" or self.inside_tag == "mark" or self.inside_tag == "strike" or self.inside_tag == "del") and self.zim_str.endswith(self.beg[self.inside_tag])):
            return
        if tag == "blockquote":
            self.inside_blockquote = True
        #If the tag a is in a non-nestable one, tag a prevails and the previous one is deleted. In block sentences it is not done
        if tag == "a" and self.inside_tag and ((self.inside_tag != "pre" and self.inside_tag != "code")):
            self.del_tag = self.inside_tag
            self.zim_str = self.zim_str[:len(self.zim_str)-len(self.start_tag)]
        #Initialize non-nestable tag
        if  tag != "td" and tag != "dd" and self.beg.get(tag) or tag == "a" and not self.inside_tag:
            self.inside_tag = tag
        if (tag == "pre" or tag == "code"): #If pre in p
            self.inside_pre = True
        if tag in list(self.beg.keys()):
            #Add blank when tag not start line
            if self.zim_str.endswith(("\n", "(", "[", "\t", "\"", " ", "/", '\xa0')):
                blank = ""
            else:
                blank = " "
            self.zim_str += blank + self.beg[tag]
            self.start_tag = self.beg[tag] #Store start tag to delete it could be somewhere else
        if tag == "p":
            self.inside_p = True
            if self.inside_blockquote:
                self.zim_str += "\t"
        elif tag == "del":
            datetime = assoc("datetime", attrs)
            if datetime is not None:
                self.tag_attrib = " (" + datetime + ")"
        elif tag == "abbr":
            title = assoc("title", attrs)
            if title is not None:
                self.tag_attrib = " (" + title + ")"
        elif tag == "q":
            cite = assoc("cite", attrs)
            if cite is not None:
                self.tag_attrib = " ([[#|" + cite + "]])"
            self.zim_str += '"'
        elif tag == "time":
            datetime = assoc("datetime", attrs)
            if datetime is not None:
                self.tag_attrib = " (" + datetime + ")"
        elif tag == "a":
            href = assoc("href", attrs)
            self.a_href = href #ref of tag
            if href is None:
                href = "#"
             #Add blank when tag not start line
            if self.zim_str.endswith(("\n", "(", "[", "\t", "\"", " ", "/", '\xa0')):
                blank = ""
            else:
                blank = " "
            #If we are in a table we escape |
            if self.inside_table:
                pipe = "\|"
            else:
                pipe = "|"
            self.zim_str += blank + "[[{}".format(href) + pipe
        elif tag == "ol":
            #if we are in a definition list the tab is not put to the dd
            if self.inside_dl and self.zim_str.endswith("\t"):
                 self.zim_str = self.zim_str[:len(self.zim_str)-len("\t")]
            #If it is not at the beginning of the line an enter is added
            if self.zim_str and not self.zim_str.endswith("\n"):
                self.zim_str += "\n"
            self.list_type = "ol"
            self.item_no = 0
            self.list_level += 1
        elif tag == "ul":
            #if we are in a definition list the tab is not put to the dd
            if self.inside_dl and self.zim_str.endswith("\t"):
                 self.zim_str = self.zim_str[:len(self.zim_str)-len("\t")]
            #If it is not at the beginning of the line an enter is added
            if self.zim_str and not self.zim_str.endswith("\n"):
                self.zim_str += "\n"
            self.list_type = "ul"
            self.item_no = 0
            self.list_level += 1
        elif tag == "li":
            #If you are in a blockquote add tab
            if self.inside_blockquote:
                self.zim_str += "\t"
            #If tag li no close add enter
            if self.inside_li and (self.zim_str and not self.zim_str.endswith("\n")):
                self.zim_str += "\n"
            self.item_no += 1
            self.zim_str += "\t" * self.list_level #Add level
            if self.list_type == "ol":
                self.zim_str += str(self.item_no) + ". "
            else:
                self.zim_str += "* "
            self.inside_li = True
        elif tag == "img":
            src = assoc("src", attrs)
            if src is None or src == "":
                src = "#"
            alt = assoc("alt", attrs)
            if alt is None:
                alt = "Image"
            if src != "#" and not self.inside_table:
                #If the image and the link match, only the image remains and the label is deleted
                if self.inside_tag == "a" and src == self.a_href:
                    self.zim_str = self.zim_str[:len(self.zim_str)-len("[[" + self.a_href + "|")]
                #Si img inside a an <> image then prevails a
                if self.inside_tag == "a" and src != self.a_href:
                    return
                qmark_index = src.find('?')
                if qmark_index < 0:
                    qmark_index = len(src)
                img_name = os.path.basename(src[:qmark_index])
                if not self.folder.exists():
                    self.folder.touch()
                get_url(src, self.folder.path + "/" + img_name)
                self.zim_str += "{{./" + img_name + "}}"
            else:
                if self.inside_table:
                    self.zim_str += "{0}".format(src)
                else:
                    self.zim_str += "[[{0}|{1}]]".format(src, alt)
        elif tag == "iframe":
            self.inside_iframe = True
            src = assoc("src", attrs)
            self.zim_str += "#|" + src
        elif tag == "span":
            self.inside_span = True
        elif tag == "dl":
            self.inside_dl = True
        elif tag == "table":
            self.inside_table = True

    def handle_endtag(self, tag):
        if self.inside_tag and tag != self.inside_tag and not (self.inside_tag == "th" or self.inside_tag == "td" or self.inside_tag == "dt" or self.inside_tag == "dd" ) and not (tag == "a" and (self.inside_tag == "b" or self.inside_tag == "strong" or self.inside_tag == "i" or self.inside_tag == "em" or self.inside_tag == "u" or self.inside_tag == "ins" or self.inside_tag == "mark" or self.inside_tag == "strike" or self.inside_tag == "del") and self.del_tag):
            return
        if tag == "blockquote":
            self.inside_blockquote = False
        #end of nestable tag
        if self.inside_tag == tag:
            self.inside_tag = "";
            #Init href of tag a
            if tag == "a":
                self.a_href = ""
        #If you tag this within another non-nestable it is deleted
        if self.del_tag == tag:
            self.start_tag = ""
            self.del_tag = ""
            return
        if (tag == "pre" or tag == "code"):
            #If tag empty del start tag
            if not self.pre_data:
                if self.zim_str.endswith("''"):
                    self.zim_str = self.zim_str[:len(self.zim_str) - 2]
                self.pre_data = ""
                self.inside_pre = False
                return
            if self.pre_data.count('\n') > 0:
                #Initial tag
                if self.zim_str.endswith("''"):
                    self.zim_str = self.zim_str[:len(self.zim_str) - 2]
                self.zim_str += "\n'''\n"
            self.zim_str += self.pre_data
            #Final Tag
            if self.pre_data.count('\n') > 0:
                self.zim_str += "\n'''\n"
            else:
                self.zim_str += self.end[tag]
            self.pre_data = ""
            self.inside_pre = False
            return
        #Remove enter before tr, td, th
        if tag == "tr" or tag == "td" or tag == "th":
            if self.zim_str.endswith("\n"):
                self.zim_str = self.zim_str[:len(self.zim_str) - len("\n")]
        if tag == "p":
            self.inside_p = False
        elif tag == "del" and self.tag_attrib:
            self.zim_str += self.tag_attrib
            self.tag_attrib = ""
        elif tag == "abbr" and self.tag_attrib:
            self.zim_str += self.tag_attrib
            self.tag_attrib = ""
        elif tag == "q":
            self.zim_str += '"'
            if self.tag_attrib:
                self.zim_str += self.tag_attrib
            if not self.inside_p:
                self.zim_str += "\n"
            self.tag_attrib = ""
        elif tag == "time" and self.tag_attrib:
            self.zim_str += self.tag_attrib
            self.tag_attrib = ""
        elif tag == "iframe":
            self.inside_iframe = False
        elif tag == "ol" or tag == "ul":
            self.list_level -= 1
        elif tag == "span":
            self.inside_span = False
        elif tag == "dl":
            self.inside_dl = False
        elif tag == "table":
            self.inside_table = False
        if tag in list(self.end.keys()):
            self.start_tag = ""
            if tag == "li":
                #If li empty del
                if self.list_type == "ul" and self.zim_str.endswith("* "):
                    self.zim_str = self.zim_str[:len(self.zim_str) - 2]
                elif self.list_type == "ol" and self.zim_str.endswith(str(self.item_no) + ". "):
                    self.zim_str = self.zim_str[:len(self.zim_str) - len(str(self.item_no) + ". ")]
                    self.item_no -= 1
                #Add enter if not exists in li tag
                elif not self.zim_str.endswith("\n"):
                    self.zim_str += "\n"
            else:
                #If we are not at a level higher than the first level of a list and not two last tag  finish in \n
                if not ((tag == "ol" or tag == "ul") and self.list_level >= 0):
                    #If tag empty then delete
                    if tag in list(self.beg.keys()) and self.beg[tag] and self.zim_str.endswith(self.beg[tag]):
                        self.zim_str = self.zim_str[:len(self.zim_str) - len(self.beg[tag])]
                    else:
                        #If not duplicate \n
                        if not ((tag == "ol" or tag == "ul") and self.zim_str.endswith("\n")):
                            self.zim_str += self.end[tag]
            #If tag li end inside_li false
            if tag == "li" or tag == "ul" or tag == "ol":
                 self.inside_li = False

    def handle_data(self, data):
        if self.inside_pre: #not clean
            self.pre_data += data
        else:
            if self.inside_iframe:
                space_removed_data = ""
            else:
                #Put as a literal syntax of zim
                data = re.sub('(\'\'.+\'\')', r"''\1''", data)
                data = re.sub('(\[\[.*\]\])', r"''\1''", data)
                data = re.sub('(^=+ .+ =+)', r"''\1''", data)
                data = re.sub('(^\t*\* )', r"''\1''", data)
                data = re.sub('(^\t*\[[ *x]\] )', r"''\1''", data)
                data = re.sub('(\*\*.+\*\*)', r"''\1''", data)
                data = re.sub('(\/\/.+\/\/)', r"''\1''", data)
                data = re.sub('(__.+__)', r"''\1''", data)
                data = re.sub('(~~.+~~)', r"''\1''", data)
                data = re.sub('(\^\{.+\})', r"''\1''", data)
                data = re.sub('(\_\{.+\})', r"''\1''", data)
                #If we are in a span tag, rstrip does not apply
                if self.inside_span:
                   space_removed_data = re.sub(r"[\s]+", " ", data)
                else:
                    space_removed_data = re.sub(r"[\s]+", " ", data.rstrip())
                    #If we are on a table they escape \ n and |
                    if self.inside_table:
                        space_removed_data = space_removed_data.replace("|", "\|")
                        space_removed_data = space_removed_data.replace("\n", "\\n")
            self.zim_str += space_removed_data

    def handle_entityref(self, name):
        if name in name2codepoint:
            c = chr(name2codepoint[name])
        if self.inside_pre:
            #Add blank when tag not start line
            if self.pre_data.endswith(("\n", "(", "[", "\t", "\"", " ", "/", '\xa0')):
                blank = ""
            else:
                blank = " "
            self.pre_data += blank + c
        else:
            #Add blank when tag not start line
            if self.zim_str.endswith(("\n", "(", "[", "\t", "\"", " ", "/", '\xa0')):
                blank = ""
            else:
                blank = " "
            self.zim_str += blank + c

    def handle_charref(self, name):
        if name.startswith('x'):
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))
        #Add blank when tag not start line
        if self.zim_str.endswith(("\n", "(", "[", "\t", "\"", " ", "/", '\xa0')):
            blank = ""
        else:
            blank = " "
        self.zim_str += blank + c

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
            if src is None or src == "":
                src = "#"
            alt = assoc("alt", attrs)
            if alt is None:
                alt = "Image"
            if src != "#" and not self.inside_table:
                #If the image and the link match, only the image remains and the label is deleted
                if self.inside_tag == "a" and src == self.a_href:
                    self.zim_str = self.zim_str[:len(self.zim_str)-len("[[" + self.a_href + "|")]
                #If img inside a an <> image then prevails a if not image_inside_a
                if self.inside_tag == "a" and src != self.a_href:
                    if self.image_inside_a:
                        self.zim_str = self.zim_str[:len(self.zim_str)-len("[[" + self.a_href + "|")]
                    else:
                        return
                qmark_index = src.find('?')
                if qmark_index < 0:
                    qmark_index = len(src)
                img_name = os.path.basename(src[:qmark_index])
                if not self.folder.exists():
                    self.folder.touch()
                get_url(src, self.folder.path + "/" + img_name)
                self.zim_str += "{{./" + img_name + "}}"
            else:
                if self.inside_table:
                    self.zim_str += "{0}".format(src)
                else:
                    self.zim_str += "[[{0}|{1}]]".format(src, alt)
        elif tag == "hr":
            self.zim_str += "-----\n"

    def to_zim(self, html_str, folder):
        self.folder = folder
        self.feed(html_str)
        #return self.zim_str.strip() + ("\n\n" if self.zim_str.strip().endswith("|") else "")
        return re.sub(r'\n\n+', "\n\n", self.zim_str).strip() + ("\n\n" if self.zim_str.strip().endswith("|") else "")
