pastefromhtml
=============

pastefromhtml is a Zim plugin that lets you paste lists, links, text, and now images (thanks to an anonymous commit) from html clipboard data. 

#### Installation

You can install pastefromhtml plugin in Zim, by creating a folder with files `htmlcdparser.py` and `__init__.py` in your zim/plugins directory. 

For installation in Linux, you can place a folder (with files `htmlcdparser.py` and `__init__.py` inside) in  `~/.local/share/zim/plugins` directory.

pastefromhtml plugin can also be installed by cloning the github repository in zim/plugins directory: 

```sh
cd ~/.local/share/zim/plugins
git clone https://github.com/cetinkaya/pastefromhtml.git
```

To enable the plugin, click on the menu entry `Edit / Preferences`, then go to `Plugins` tab. 


#### Use

pastefromhtml adds menu entries (`Tools / Paste from HTML`, `Edit / Paste from HTML`) and a right-click context-menu entry, as well as a keyboard shortcut (`ctrl + shift + v`) in Zim. 

After you copy lists/links/text/images in your browser, paste them into Zim by clicking on the menu entry or by using the shortcut `ctrl + shift + v`.


#### Quirks

##### Images inside anchor tags

When pasting image tags `<img>` that are placed inside anchor tags `<a>`, the default behavior of pastefromhtml is to only paste the URL that the anchor tag refers to (unless it is the URL of the image). There is an option that can be configured so as to paste the images instead of URLs of the anchor tags. To access this option, you can click on Edit/Preferences in the menu bar, navigate to the Plugins tab, and select Paste from HTML. After that, click on the Configure button located on the right-hand side.
