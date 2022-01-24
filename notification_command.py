import subprocess

from gi.repository import Gtk
from gi.repository import GObject

from gajim.common import app
from gajim.plugins import GajimPlugin
from gajim.plugins.helpers import log_calls
from gajim.plugins.gui import GajimPluginConfigDialog

# Since Gajim 1.1.0 _() has to be imported
try:
    from gajim.common.i18n import _
except ImportError:
    pass

class NotificationCommand(GajimPlugin):
    @log_calls('NotificationCommand')
    def init(self):
        self.description = _('Start a command when getting a message. Start a different one upon read.')
        self.config_dialog = NotificationCommandPluginConfigDialog(self)
        self.config_default_values = {
            'command1': ("xset led named 'Scroll Lock'", ''),
            'command2': ("xset -led named 'Scroll Lock'", ''),
        }
        self.is_active = None
        self.id_0 = None

    def on_event_added(self, event):
        if event.show_in_systray:
            self.cmd_trigger()

    def on_event_removed(self, event_list):
        self.cmd_trigger()

    def cmd_trigger(self):
        if app.events.get_nb_systray_events():
            self.led_on()
        else:
            self.led_off()
    
    def led_on(self):
        if self.id_0 is None:
            subprocess.Popen('%s' % self.config['command1'], shell=True).wait()
            self.id_0 = True
        return True

    def led_off(self):
        if self.id_0:
            subprocess.Popen('%s' % self.config['command2'], shell=True).wait()
            self.id_0 = None

    @log_calls('NotificationCommand')
    def activate(self):
        app.events.event_added_subscribe(self.on_event_added)
        app.events.event_removed_subscribe(self.on_event_removed)
        if app.events.get_nb_systray_events():
            self.led_on()
            

    @log_calls('NotificationCommand')
    def deactivate(self):
        app.events.event_added_unsubscribe(self.on_event_added)
        app.events.event_removed_unsubscribe(self.on_event_removed)
        self.led_off()


class NotificationCommandPluginConfigDialog(GajimPluginConfigDialog):
    def init(self):
        self.GTK_BUILDER_FILE_PATH = self.plugin.local_file_path(
            'config_dialog.ui')
        self.xml = Gtk.Builder()
        self.xml.set_translation_domain('gajim_plugins')
        self.xml.add_objects_from_file(self.GTK_BUILDER_FILE_PATH,
            ['config_table'])
        config_table = self.xml.get_object('config_table')
        self.get_child().pack_start(config_table, True, True, 0)
        self.xml.connect_signals(self)

    def on_run(self):
        self.isactive = self.plugin.active
        if self.plugin.active:
            app.plugin_manager.deactivate_plugin(self.plugin)
        for name in ('command1', 'command2'):
            widget = self.xml.get_object(name)
            widget.set_text(self.plugin.config[name])

    def on_close_button_clicked(self, widget):
        widget = self.xml.get_object('command1')
        self.plugin.config['command1'] = widget.get_text()
        widget = self.xml.get_object('command2')
        self.plugin.config['command2'] = widget.get_text()
        if self.isactive:
            app.plugin_manager.activate_plugin(self.plugin)
        GajimPluginConfigDialog.on_close_button_clicked(self, widget)
