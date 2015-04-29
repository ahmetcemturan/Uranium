from PyQt5.QtCore import pyqtSlot, pyqtProperty, pyqtSignal, QObject, QVariant

from UM.Application import Application
from UM.PluginRegistry import PluginRegistry

import os.path

class ActiveViewProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._active_view = None
        Application.getInstance().getController().activeViewChanged.connect(self._onActiveViewChanged)
        self._onActiveViewChanged()
        
    activeViewChanged = pyqtSignal()
    
    @pyqtProperty(str, notify = activeViewChanged)
    def activeViewPanel(self):
        if not self._active_view:
            return ""

        try:
            panel_file = PluginRegistry.getInstance().getMetaData(self._active_view.getPluginId())['view']['view_panel']
        except KeyError:
            return ""

        return os.path.join(PluginRegistry.getInstance().getPluginPath(self._active_view.getPluginId()), panel_file)
    
    @pyqtSlot(str, QVariant)
    def triggerAction(self, action, data):
        if not self._active_view:
            return

        action = getattr(self._active_view, action)
        if action:
            action(data)
    
    @pyqtProperty(bool, notify = activeViewChanged)
    def valid(self):
        return self._active_view != None
    
    def _onActiveViewChanged(self):
        self._active_view = Application.getInstance().getController().getActiveView()
        self.activeViewChanged.emit()

def createActiveViewProxy(engine, script_engine):
    return ActiveViewProxy()