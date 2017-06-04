"""Support command."""
import sublime
import sublime_plugin
import textwrap
import webbrowser
import re

__version__ = "3.4.0"
__pc_name__ = 'RegReplace'

CSS = '''
div.reg-replace { padding: 10px; margin: 0; }
.reg-replace h1, .reg-replace h2, .reg-replace h3,
.reg-replace h4, .reg-replace h5, .reg-replace h6 {
    {{'.string'|css}}
}
.reg-replace blockquote { {{'.comment'|css}} }
.reg-replace a { text-decoration: none; }
'''


def list2string(obj):
    """Convert list to string."""

    return '.'.join([str(x) for x in obj])


def format_version(module, attr, call=False):
    """Format the version."""

    try:
        if call:
            version = getattr(module, attr)()
        else:
            version = getattr(module, attr)
    except Exception as e:
        print(e)
        version = 'Version could not be acquired!'

    if not isinstance(version, str):
        version = list2string(version)
    return version


def is_installed_by_package_control():
    """Check if installed by package control."""

    settings = sublime.load_settings('Package Control.sublime-settings')
    return str(__pc_name__ in set(settings.get('installed_packages', [])))


class RegReplaceSupportInfoCommand(sublime_plugin.ApplicationCommand):
    """Support info."""

    def run(self):
        """Run command."""

        info = {}

        info["platform"] = sublime.platform()
        info["version"] = sublime.version()
        info["arch"] = sublime.arch()
        info["plugin_version"] = __version__
        info["pc_install"] = is_installed_by_package_control()
        try:
            import mdpopups
            info["mdpopups_version"] = format_version(mdpopups, 'version', call=True)
        except Exception:
            info["mdpopups_version"] = 'Version could not be acquired!'

        try:
            import backrefs
            info["backrefs_version"] = format_version(backrefs, 'version')
        except Exception:
            info["backrefs_version"] = 'Version could not be acquired!'

        try:
            import regex
            info["regex_version"] = format_version(regex, '__version__')
        except Exception:
            info["regex_version"] = 'Version could not be acquired!'

        try:
            import markdown
            info["markdown_version"] = format_version(markdown, 'version')
        except Exception:
            info["markdown_version"] = 'Version could not be acquired!'

        try:
            import jinja2
            info["jinja_version"] = format_version(jinja2, '__version__')
        except Exception:
            info["jinja_version"] = 'Version could not be acquired!'

        try:
            import pygments
            info["pygments_version"] = format_version(pygments, '__version__')
        except Exception:
            info["pygments_version"] = 'Version could not be acquired!'

        msg = textwrap.dedent(
            """\
            - ST ver.: %(version)s
            - Platform: %(platform)s
            - Arch: %(arch)s
            - Plugin ver.: %(plugin_version)s
            - Install via PC: %(pc_install)s
            - mdpopups ver.: %(mdpopups_version)s
            - backrefs ver.: %(backrefs_version)s
            - regex ver.: %(regex_version)s
            - markdown ver.: %(markdown_version)s
            - pygments ver.: %(pygments_version)s
            - jinja2 ver.: %(jinja_version)s
            """ % info
        )

        sublime.message_dialog(msg + '\nInfo has been copied to the clipboard.')
        sublime.set_clipboard(msg)


class RegReplaceOpenSiteCommand(sublime_plugin.ApplicationCommand):
    """Open site links."""

    def run(self, url):
        """Open the url."""

        webbrowser.open_new_tab(url)


class RegReplaceDocCommand(sublime_plugin.WindowCommand):
    """Open doc page."""

    re_pkgs = re.compile(r'^Packages')

    def on_navigate(self, href):
        """Handle links."""

        if href.startswith('sub://Packages'):
            sublime.run_command('open_file', {"file": self.re_pkgs.sub('${packages}', href[6:])})
        else:
            webbrowser.open_new_tab(href)

    def run(self, page):
        """Open page."""

        try:
            import mdpopups
            has_phantom_support = (mdpopups.version() >= (1, 10, 0)) and (int(sublime.version()) >= 3124)
        except Exception:
            has_phantom_support = False

        if not has_phantom_support:
            sublime.run_command('open_file', {"file": page})
        else:
            text = sublime.load_resource(page.replace('${packages}', 'Packages'))
            view = self.window.new_file()
            view.set_name('RegReplace - Quick Start')
            view.settings().set('gutter', False)
            view.settings().set('word_wrap', False)
            if has_phantom_support:
                mdpopups.add_phantom(
                    view,
                    'quickstart',
                    sublime.Region(0),
                    text,
                    sublime.LAYOUT_INLINE,
                    css=CSS,
                    wrapper_class="reg-replace",
                    on_navigate=self.on_navigate
                )
            else:
                view.run_command('insert', {"characters": text})
            view.set_read_only(True)
            view.set_scratch(True)


class RegReplaceChangesCommand(sublime_plugin.WindowCommand):
    """Changelog command."""

    def run(self):
        """Show the changelog in a new view."""
        try:
            import mdpopups
            has_phantom_support = (mdpopups.version() >= (1, 10, 0)) and (int(sublime.version()) >= 3124)
        except Exception:
            has_phantom_support = False

        text = sublime.load_resource('Packages/RegReplace/CHANGES.md')
        view = self.window.new_file()
        view.set_name('RegReplace - Changelog')
        view.settings().set('gutter', False)
        view.settings().set('word_wrap', False)
        if has_phantom_support:
            mdpopups.add_phantom(
                view,
                'changelog',
                sublime.Region(0),
                text,
                sublime.LAYOUT_INLINE,
                wrapper_class="reg-replace",
                css=CSS,
                on_navigate=self.on_navigate
            )
        else:
            view.run_command('insert', {"characters": text})
        view.set_read_only(True)
        view.set_scratch(True)

    def on_navigate(self, href):
        """Open links."""
        webbrowser.open_new_tab(href)
