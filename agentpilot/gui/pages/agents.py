
import json

from PySide6.QtWidgets import *

from agentpilot.utils.helpers import path_to_pixmap, block_signals, display_messagebox, block_pin_mode
from agentpilot.utils import sql

from agentpilot.gui.components.agent_settings import AgentSettings
from agentpilot.gui.components.config import ConfigTreeWidget
from gui.widgets.base import ContentPage


class Page_Agents(ContentPage):
    def __init__(self, main):
        super().__init__(main=main, title='Agents')
        self.main = main
        self.tree_config = ConfigTreeWidget(
            parent=self,
            db_table='agents',
            db_config_field='config',
            query="""
                SELECT
                    id,
                    json_extract(config, '$."general.avatar_path"') AS avatar,
                    config,
                    json_extract(config, '$."general.name"') AS name,
                    '' AS chat_button
                FROM agents
                ORDER BY id DESC""",
            schema=[
                {
                    'text': 'id',
                    'key': 'id',
                    'type': int,
                    'visible': False,
                    # 'readonly': True,
                },
                {
                    'key': 'avatar',
                    'text': '',
                    'type': str,
                    'visible': False,
                },
                {
                    'text': 'Config',
                    'type': str,
                    'visible': False,
                },
                {
                    'text': 'Name',
                    'key': 'name',
                    'type': str,
                    'stretch': True,
                    'image_key': 'avatar',
                },
                {
                    'text': '',
                    'type': QPushButton,
                    'icon': ':/resources/icon-chat.png',
                    'func': self.on_chat_btn_clicked,
                    'width': 45,
                },
            ],
            add_item_prompt=('Add Agent', 'Enter a name for the agent:'),
            del_item_prompt=('Delete Agent', 'Are you sure you want to delete this agent?'),
            layout_type=QVBoxLayout,
            config_widget=self.Agent_Config_Widget(parent=self),
            tree_width=600,
            tree_header_hidden=True,
        )
        self.tree_config.build_schema()

        self.tree_config.tree.itemDoubleClicked.connect(self.on_row_double_clicked)

        self.layout.addWidget(self.tree_config)
        self.layout.addStretch(1)

    class Agent_Config_Widget(AgentSettings):
        def __init__(self, parent):
            super().__init__(parent=parent)
            self.parent = parent

        def save_config(self):
            """Saves the config to database when modified"""
            item = self.parent.tree_config.tree.currentItem()
            if not item:
                return False

            id = int(item.text(0))
            json_config = json.dumps(self.config)
            name = self.config.get('general.name', 'Assistant')
            sql.execute("UPDATE agents SET config = ?, name = ? WHERE id = ?", (json_config, name, id))
            self.settings_sidebar.load()

    def load(self):
        self.tree_config.load()

    def on_row_double_clicked(self):
        item = self.tree_config.tree.currentItem()
        if not item:
            return False
        id = int(item.text(0))
        self.chat_with_agent(id)

    def on_chat_btn_clicked(self, row_data):
        id_value = row_data[0]  # self.table_widget.item(row_item, 0).text()
        self.chat_with_agent(id_value)

    def chat_with_agent(self, id):
        if self.main.page_chat.context.responding:
            return
        self.main.page_chat.new_context(agent_id=id)
        self.main.sidebar.btn_new_context.click()


    # #     super().__init__(
    # #         parent=main,
    # #         db_table='blocks',
    # #         db_config_field='config',
    # #         query="""
    # #             SELECT
    # #                 id,
    # #                 name
    # #             FROM blocks""",
    # #         schema=[
    # #             {
    # #                 'text': 'id',
    # #                 'key': 'id',
    # #                 'type': int,
    # #                 'visible': False,
    # #                 # 'readonly': True,
    # #             },
    # #             {
    # #                 'text': 'Name',
    # #                 'key': 'name',
    # #                 'type': str,
    # #                 # 'width': 200,
    # #             },
    # #         ],
    # #         add_item_prompt=('Add Block', 'Enter a placeholder tag for the block:'),
    # #         del_item_prompt=('Delete Block', 'Are you sure you want to delete this block?'),
    # #         readonly=False,
    # #         layout_type=QHBoxLayout,
    # #         config_widget=AgentSettings(parent=self),
    # #         tree_width=150,
    # #     )
    # #     self.main = main
    # #     self.build_schema()
    # #     # self.parent = parent
    # #
    # # def field_edited(self, item):
    # #     super().field_edited(item)
    # #
    # #     # reload blocks
    # #     self.parent.main.system.blocks.load()
    # #
    # # def add_item(self):
    # #     if not super().add_item():
    # #         return
    # #     self.load()
    # #     self.parent.main.system.blocks.load()
    # #
    # # def delete_item(self):
    # #     if not super().delete_item():
    # #         return
    # #     self.load()
    # #     self.parent.main.system.blocks.load()
    # #
    # # # class Agent_Config_Widget(AgentSettings):
    # # #     def __init__(self, *args, **kwargs):
    # # #         super().__init__(*args, **kwargs)
    # # #         pass
    #
    #     self.main = main
    #
    #     self.btn_new_agent = self.Button_New_Agent(parent=self)
    #     self.title_layout.addWidget(self.btn_new_agent)  # QPushButton("Add", self))
    #
    #     self.title_layout.addStretch()
    #
    #     # Adding input layout to the main layout
    #     self.tree = BaseTreeWidget(self)
    #     self.tree.setColumnCount(6)
    #     self.tree.setColumnWidth(1, 20)
    #     self.tree.setColumnWidth(4, 45)
    #     self.tree.setColumnWidth(5, 45)
    #     self.tree.header().setSectionResizeMode(3, QHeaderView.Stretch)
    #     self.tree.setSortingEnabled(True)
    #     self.tree.hideColumn(0)
    #     self.tree.hideColumn(2)
    #     # self.table_widget.horizontalHeader().hide()
    #     self.tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
    #     # connect on_agent_selected to tree view selection change
    #     self.tree.itemSelectionChanged.connect(self.on_agent_selected)
    #     self.tree.header().hide()
    #
    #     # Connect the double-click signal with the chat button click
    #     self.tree.itemDoubleClicked.connect(self.on_row_double_clicked)
    #
    #     self.agent_settings = AgentSettings(self)
    #
    #     # Add table and container to the layout
    #     self.layout.addWidget(self.tree)
    #     self.layout.addWidget(self.agent_settings)
    #
    # def load(self):  # Load agents
    #     icon_chat = QIcon(':/resources/icon-chat.png')
    #     icon_del = QIcon(':/resources/icon-delete.png')
    #
    #     with block_signals(self.tree):
    #         self.tree.clear()  # Clear entire tree widget
    #         data = sql.get_results("""
    #             SELECT
    #                 id,
    #                 '' AS avatar,
    #                 config,
    #                 '' AS name,
    #                 '' AS chat_button,
    #                 '' AS del_button
    #             FROM agents
    #             ORDER BY id DESC""")
    #         for row_data in data:
    #             r_config = json.loads(row_data[2])
    #             agent_name = r_config.get('general.name', 'Assistant')
    #
    #             # Create a new tree widget item
    #             item = QTreeWidgetItem(self.tree, [
    #                 str(row_data[0]),  # ID
    #                 '',  # Avatar placeholder
    #                 row_data[2],  # Config
    #                 agent_name,  # Name
    #                 '',  # Chat button placeholder
    #                 ''  # Delete button placeholder
    #             ])
    #
    #             # Parse the config JSON to get the avatar path
    #             agent_avatar_path = r_config.get('general.avatar_path', '')
    #             pixmap = path_to_pixmap(agent_avatar_path, diameter=25)
    #
    #             # Create a QLabel to hold the pixmap
    #             avatar_label = QLabel()
    #             avatar_label.setPixmap(pixmap)
    #             # set background to transparent
    #             avatar_label.setAttribute(Qt.WA_TranslucentBackground, True)
    #
    #             # Set the avatar as the icon for the item with the id
    #             item.setIcon(1, QIcon(pixmap))
    #
    #             # Create buttons for Chat and Delete
    #             btn_chat_func = partial(self.on_chat_btn_clicked, row_data)
    #             self.tree.setItemIconButtonColumn(item, 4, icon_chat, btn_chat_func)
    #
    #             btn_del_func = partial(self.delete_agent, row_data)
    #             self.tree.setItemIconButtonColumn(item, 5, icon_del, btn_del_func)
    #
    #     # Selecting an item if a specific condition is met
    #     if self.agent_settings.agent_id > 0:
    #         root = self.tree.invisibleRootItem()
    #         for i in range(root.childCount()):
    #             if root.child(i).text(0) == str(self.agent_settings.agent_id):
    #                 self.tree.setCurrentItem(root.child(i))
    #                 break
    #     else:
    #         if self.tree.topLevelItemCount() > 0:
    #             self.tree.setCurrentItem(self.tree.topLevelItem(0))
    #
    #     pass  # above is tree, below is table
    #     # with block_signals(self):
    #     #     self.table_widget.setRowCount(0)
    #     #     data = sql.get_results("""
    #     #         SELECT
    #     #             id,
    #     #             '' AS avatar,
    #     #             config,
    #     #             '' AS name,
    #     #             '' AS chat_button,
    #     #             '' AS del_button
    #     #         FROM agents
    #     #         ORDER BY id DESC""")
    #     #     for row_data in data:
    #     #         row_data = list(row_data)
    #     #         r_config = json.loads(row_data[2])
    #     #         row_data[3] = r_config.get('general.name', 'Assistant')
    #     #
    #     #         row_position = self.table_widget.rowCount()
    #     #         self.table_widget.insertRow(row_position)
    #     #         for column, item in enumerate(row_data):
    #     #             self.table_widget.setItem(row_position, column, QTableWidgetItem(str(item)))
    #     #
    #     #         # Parse the config JSON to get the avatar path
    #     #         agent_avatar_path = r_config.get('general.avatar_path', '')
    #     #         pixmap = path_to_pixmap(agent_avatar_path, diameter=25)
    #     #
    #     #         # Create a QLabel to hold the pixmap
    #     #         avatar_label = QLabel()
    #     #         avatar_label.setPixmap(pixmap)
    #     #         # set background to transparent
    #     #         avatar_label.setAttribute(Qt.WA_TranslucentBackground, True)
    #     #
    #     #         # Add the new avatar icon column after the ID column
    #     #         self.table_widget.setCellWidget(row_position, 1, avatar_label)
    #     #
    #     #         btn_chat = QPushButton('')
    #     #         btn_chat.setIcon(icon_chat)
    #     #         btn_chat.setIconSize(QSize(25, 25))
    #     #         # set background to transparent
    #     #         # set background to white at 30% opacity when hovered
    #     #         btn_chat.setStyleSheet("QPushButton { background-color: transparent; }"
    #     #                                "QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); }")
    #     #         btn_chat.clicked.connect(partial(self.on_chat_btn_clicked, row_data))
    #     #         self.table_widget.setCellWidget(row_position, 4, btn_chat)
    #     #
    #     #         btn_del = QPushButton('')
    #     #         btn_del.setIcon(icon_del)
    #     #         btn_del.setIconSize(QSize(25, 25))
    #     #         btn_del.setStyleSheet("QPushButton { background-color: transparent; }"
    #     #                               "QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); }")
    #     #         btn_del.clicked.connect(partial(self.delete_agent, row_data))
    #     #         self.table_widget.setCellWidget(row_position, 5, btn_del)
    #     #
    #     # if self.agent_settings.agent_id > 0:
    #     #     for row in range(self.table_widget.rowCount()):
    #     #         if self.table_widget.item(row, 0).text() == str(self.agent_settings.agent_id):
    #     #             self.table_widget.selectRow(row)
    #     #             break
    #     # else:
    #     #     if self.table_widget.rowCount() > 0:
    #     #         self.table_widget.selectRow(0)
    #
    # def on_row_double_clicked(self, item):
    #     id = int(item.text(0))
    #     self.chat_with_agent(id)
    #
    # def on_agent_selected(self):
    #     current_item = self.tree.currentItem()
    #     if not current_item or current_item.parent() is not None:  # Check if not a top-level item
    #         return
    #
    #     agent_id = int(current_item.text(0))
    #     self.agent_settings.agent_id = agent_id
    #     agent_json_config = sql.get_scalar('SELECT config FROM agents WHERE id = ?', (agent_id,))
    #     self.agent_settings.load_config(agent_json_config)
    #     self.agent_settings.load()
    #
    #     ###################
    #     # current_row = self.table_widget.currentRow()
    #     # if current_row == -1: return
    #     # sel_id = self.table_widget.item(current_row, 0).text()
    #     # agent_config_json = sql.get_scalar('SELECT config FROM agents WHERE id = ?', (sel_id,))
    #     #
    #     # self.agent_settings.agent_id = int(self.table_widget.item(current_row, 0).text())
    #     # self.agent_settings.agent_config = json.loads(agent_config_json) if agent_config_json else {}
    #     # self.agent_settings.load()
    #
    # def on_chat_btn_clicked(self, row_data):
    #     id_value = row_data[0]  # self.table_widget.item(row_item, 0).text()
    #     self.chat_with_agent(id_value)
    #
    # def chat_with_agent(self, id):
    #     if self.main.page_chat.context.responding:
    #         return
    #     self.main.page_chat.new_context(agent_id=id)
    #     self.main.sidebar.btn_new_context.click()
    #
    # def delete_agent(self, row_data):
    #     context_count = sql.get_scalar("""
    #         SELECT
    #             COUNT(*)
    #         FROM contexts_members
    #         WHERE agent_id = ?""", (row_data[0],))
    #
    #     if context_count > 0:
    #         retval = display_messagebox(
    #             icon=QMessageBox.Warning,
    #             text=f"Cannot delete '{row_data[3]}' because they exist in {context_count} contexts.",
    #             title="Warning",
    #             buttons=QMessageBox.Ok,
    #         )
    #     else:
    #         retval = display_messagebox(
    #             icon=QMessageBox.Warning,
    #             text="Are you sure you want to delete this agent?",
    #             title="Delete Agent",
    #             buttons=QMessageBox.Yes | QMessageBox.No,
    #         )
    #
    #     if retval != QMessageBox.Yes:
    #         return
    #
    #     # sql.execute("DELETE FROM contexts_messages WHERE context_id IN (SELECT id FROM contexts WHERE agent_id = ?);", (row_data[0],))
    #     # sql.execute("DELETE FROM contexts WHERE agent_id = ?;", (row_data[0],))
    #     # sql.execute('DELETE FROM contexts_members WHERE context_id = ?', (row_data[0],))
    #     sql.execute("DELETE FROM agents WHERE id = ?;", (row_data[0],))
    #     self.load()
    #
    # class Button_New_Agent(IconButton):
    #     def __init__(self, parent):
    #         super().__init__(parent=parent, icon_path=':/resources/icon-new.png')
    #         self.clicked.connect(self.new_agent)
    #
    #     def new_agent(self):
    #         with block_pin_mode():
    #             text, ok = QInputDialog.getText(self, 'New Agent', 'Enter a name for the agent:')
    #
    #         if ok:
    #             global_config_str = sql.get_scalar("SELECT value FROM settings WHERE field = 'global_config'")
    #             global_conf = json.loads(global_config_str)
    #             global_conf['general.name'] = text
    #             global_config_str = json.dumps(global_conf)
    #             try:
    #                 sql.execute("INSERT INTO `agents` (`name`, `config`) SELECT ?, ?",
    #                             (text, global_config_str))
    #                 self.parent.load()
    #             except IntegrityError:
    #                 QMessageBox.warning(self, "Duplicate Agent Name", "An agent with this name already exists.")