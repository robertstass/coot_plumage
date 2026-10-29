# -*- coding: utf-8 -*-
# Compatibility layer so the coot_plumage scripts run in Coot 0.9.x (Python 2, GTK2) and Coot 1.x (Python 3, GTK3/4).
# This is not a standalone script. It is imported by plumage.py and by the scripts in coot_bin:
#     import plumage_compat as pc
# plumage.py calls plumage_compat.init(COOT_VERSION) once; every other script then reads the same value from here
# (a module is only ever imported once per Coot session, so they all share it).
# Part of coot_plumage (github.com/robertstass/coot_plumage). Written by Robert Stass, Bowden group, STRUBI/OPIC (2024)

import os
import sys

try:
    import __main__ as _main
except ImportError:
    _main = None

COOT_VERSION = None  # 0 (Coot 0.9.x and older) or 1 (Coot 1.x). Set by init().
TOOLBAR_SHOW_LABELS = True  # Coot 1 only. True: toolbar buttons show the icon and the label. False: icon only (the label is used if there is no icon).
TOOLBAR_ICON_SIZE = 24      # Coot 1 only. Icon size in pixels.


class _CootNamespace(object):
    """Attribute access to Coot's functions, i.e. pc.coot.set_map_radius_em(20).
    Looks in the 'coot' module first (this is where all the functions live in Coot 1 and also in 0.9),
    then falls back to the main namespace (where Coot 0.9 puts the python-level helper functions)."""

    def __getattr__(self, name):
        import coot as _coot_module
        try:
            return getattr(_coot_module, name)
        except AttributeError:
            pass
        if _main is not None and hasattr(_main, name):
            return getattr(_main, name)
        raise AttributeError("Coot function '%s' not found (COOT_VERSION = %s)." % (name, COOT_VERSION))


coot = _CootNamespace()

# Strong references to key binding callbacks. Some Coot 1 builds don't keep their own reference to the python function,
# so without this the function can be garbage collected and pressing the key then crashes Coot.
_keep_alive = []


def detect_version():
    """Guess the Coot version from the API that is present. Returns 1 or 0."""
    try:
        import coot as _coot_module
        if hasattr(_coot_module, "add_key_binding_gtk4_py") or hasattr(_coot_module, "add_key_binding_gtk3_py"):
            return 1
        return 0
    except ImportError:
        pass
    return 1 if sys.version_info[0] >= 3 else 0


def init(version=None, toolbar_labels=True):
    """Set the Coot version. version can be 0, 1 or None/"auto" (auto-detect).
    If a version is given explicitly but looks wrong for this Coot, a warning is printed (the explicit value is still used).
    toolbar_labels: In Coot 1, show the text label next to the icon on toolbar buttons (False = icon only)."""
    global COOT_VERSION, TOOLBAR_SHOW_LABELS
    TOOLBAR_SHOW_LABELS = bool(toolbar_labels)
    detected = detect_version()
    if version is None or str(version).lower() == "auto":
        COOT_VERSION = detected
    else:
        COOT_VERSION = int(version)
        if COOT_VERSION != detected:
            print("coot_plumage WARNING: COOT_VERSION is set to %d in plumage.py but this looks like Coot version %d. "
                  "Check the COOT_VERSION setting (or set it to None to auto-detect)." % (COOT_VERSION, detected))
    print("coot_plumage: using Coot version %d settings." % COOT_VERSION)
    return COOT_VERSION


def _require_init():
    if COOT_VERSION is None:
        init(None)


# ------------------------------------------------------------------------------------------------
# Wrappers for things that differ between versions
# ------------------------------------------------------------------------------------------------

def sphere_refine():
    """Refine the active residue and its neighbours (the same as Coot's own sphere_refine)."""
    _require_init()
    if COOT_VERSION >= 1:
        import coot_fitting
        return coot_fitting.sphere_refine()
    # Coot 0.9 puts sphere_refine in the main namespace.
    func = getattr(_main, "sphere_refine", None)
    if func is None:
        import fitting
        func = fitting.sphere_refine
    return func()


def _find_icon_image(Gtk, coot_gui, toolbar, icon, size):
    """Return a Gtk.Image for icon, or None if it can't be found. icon can be:
       - the full path to an image file (svg or png)
       - the name of an icon, with or without the extension (e.g. "refine-1" or "refine-1.svg"). Coot registers its own
         icons (the files in its pixmaps directory) with GTK, so any of those can be used, as can the standard theme icons.
       Returns None (so the button just shows its text label) if nothing is found."""
    if not icon:
        return None
    try:
        path = None
        if os.path.isfile(icon):
            path = icon
        else:
            name = icon
            if os.path.splitext(icon)[1].lower() in (".svg", ".png", ".xpm"):
                name = os.path.splitext(os.path.basename(icon))[0]
            theme = Gtk.IconTheme.get_for_display(toolbar.get_display())
            if theme.has_icon(name):
                image = Gtk.Image.new_from_icon_name(name)
                image.set_pixel_size(size)
                return image
            # Not known to the icon theme: look in Coot's pixmaps directory.
            pixmaps_dir = os.getenv("COOT_PIXMAPS_DIR") or os.path.join(coot.get_pkgdatadir_py(), "pixmaps")
            for extension in (".svg", ".png"):
                candidate = os.path.join(pixmaps_dir, name + extension)
                if os.path.isfile(candidate):
                    path = candidate
                    break
        if path is None:
            print("coot_plumage: icon '%s' not found, using a text label instead." % icon)
            return None
        gio_file = coot_gui.Gio.File.new_for_path(path)
        image = Gtk.Image.new_from_gicon(coot_gui.Gio.FileIcon.new(gio_file))
        image.set_pixel_size(size)
        return image
    except Exception as e:
        print("coot_plumage: could not load icon '%s' (%s), using a text label instead." % (icon, e))
        return None


def _toolbar_button_coot1(label, func, icon, tooltip, show_label):
    """Add a plain GTK button to Coot 1's main toolbar.
    Coot's own coot_gui.coot_toolbar_button() can't be used here: it first calls coot_gui.toolbar_label_list(), which calls
    get_label() on every child of the toolbar, and that fails ("'Box' object has no attribute 'get_label'")
    because the toolbar also contains non-button widgets. So we add the button ourselves."""
    import traceback
    import coot_gui
    Gtk = getattr(coot_gui, "Gtk", None)
    if Gtk is None:
        from gi.repository import Gtk
    toolbar = coot_gui.coot_gui_api.main_toolbar()

    def on_clicked(_widget):
        try:
            func()
        except Exception:
            print("coot_plumage: error in toolbar button '%s':" % label)
            traceback.print_exc()

    # Keep track of our buttons so that running plumage.py again replaces the callback rather than adding a duplicate button.
    registry = getattr(toolbar, "plumage_buttons", None)
    if registry is None:
        registry = {}
        toolbar.plumage_buttons = registry
    if label in registry:
        button, handler_id = registry[label]
        button.disconnect(handler_id)
    else:
        image = _find_icon_image(Gtk, coot_gui, toolbar, icon, TOOLBAR_ICON_SIZE)
        if image is None:
            button = Gtk.Button(label=label)
        else:
            button = Gtk.Button()
            if show_label:
                content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
                content.append(image)
                content.append(Gtk.Label(label=label))
                button.set_child(content)
            else:
                button.set_child(image)
        toolbar.append(button)
    if tooltip or icon:
        button.set_tooltip_text(tooltip if tooltip else label)
    registry[label] = (button, button.connect("clicked", on_clicked))
    return button


def toolbar_button(label, func, icon=None, tooltip=None, show_label=None):
    """Add a button to the Coot toolbar that calls func() (a python callable) when clicked.
    icon: the name of a Coot icon (e.g. "refine-1.svg", see Coot's pixmaps directory) or the full path to an svg/png file.
    show_label: Coot 1 only. Show the label next to the icon (default is set by the toolbar_labels option of init()).
    In Coot 0.9 the icon and tooltip are used and the button is icon only (that is how Coot 0.9 shows toolbar buttons)."""
    _require_init()
    if COOT_VERSION >= 1:
        return _toolbar_button_coot1(label, func, icon, tooltip, TOOLBAR_SHOW_LABELS if show_label is None else show_label)
    return _main.coot_toolbar_button(label, func, icon if icon else False, tooltip if tooltip else False)


def add_key_binding(name, key, func, key_code=None):
    """Bind a key to func (called with no arguments).
    key is the character (e.g. 'z' or '!'). For keys that can't be given as a plain ascii character
    (e.g. u'£'), also supply key_code, the numeric key value (the 'Key 163 not found in (python) key bindings'
    message printed by Coot 0.9 tells you this number; in Coot 1 it is the GDK keyval, e.g. 163 for the pound sign)."""
    _require_init()
    if COOT_VERSION >= 1:
        import coot as _coot_module
        adder = getattr(_coot_module, "add_key_binding_gtk4_py", None) or getattr(_coot_module, "add_key_binding_gtk3_py")

        def checked_func():
            try:
                return func()
            except Exception:
                import traceback
                print("coot_plumage: error in key binding '%s':" % name)
                traceback.print_exc()
        _keep_alive.append(checked_func)
        adder(key_code if key_code is not None else key, 0, checked_func, name)
    else:
        if key_code is not None:
            _main.key_bindings.append([key_code, key, name, func])
        else:
            _main.add_key_binding(name, key, func)


def idle_add(interval_ms, func):
    """Call func() every interval_ms milliseconds in Coot's main (GUI) thread, for as long as func returns True."""
    _require_init()
    if COOT_VERSION >= 1:
        try:
            from gi.repository import GLib
            return GLib.timeout_add(interval_ms, func)
        except ImportError:
            import gobject
            return gobject.timeout_add(interval_ms, func)
    try:
        import gobject
        return gobject.timeout_add(interval_ms, func)
    except ImportError:
        from gi.repository import GLib
        return GLib.timeout_add(interval_ms, func)
