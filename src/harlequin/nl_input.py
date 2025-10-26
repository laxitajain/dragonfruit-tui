# from __future__ import annotations

# from typing import List, Union

# from rich.text import TextType
# from sqlfmt.api import Mode, format_string
# from sqlfmt.exception import SqlfmtError
# from textual.css.query import NoMatches
# from textual.message import Message
# from textual.reactive import reactive
# from textual.widgets import ContentSwitcher, TabbedContent, TabPane, Tabs, Input
# from textual.widgets.text_area import Selection
# from textual_textarea import TextAreaSaved, TextEditor

# from harlequin.autocomplete import MemberCompleter, WordCompleter
# from harlequin.components.error_modal import ErrorModal
# from harlequin.editor_cache import BufferState, load_cache
# from harlequin.messages import WidgetMounted


# # class NlInput(Horizontal):
# #     def compose(self) -> None:
# #         yield Input(placeholder="Natural Language Query", id="nl_query_input")

# class NlInput(TabbedContent):
#     BORDER_TITLE = "Enter your query in English"
#     theme: reactive[str] = reactive("dragonfruit_tui")

#     class EditorSwitched(Message):
#         def __init__(self, active_editor: Union[CodeEditor, None]) -> None:
#             self.active_editor = active_editor
#             super().__init__()

#     def __init__(
#         self,
#         *titles: TextType,
#         initial: str = "",
#         name: Union[str, None] = None,
#         id: Union[str, None] = None,  # noqa: A002
#         classes: Union[str, None] = None,
#         disabled: bool = False,
#         language: str = "sql",
#         theme: str = "dragonfruit_tui",
#     ):
#         super().__init__(
#             *titles,
#             initial=initial,
#             name=name,
#             id=id,
#             classes=classes,
#             disabled=disabled,
#         )
#         self.language = language
#         self.theme = theme
#         self.counter = 0
#         self._word_completer: WordCompleter | None = None
#         self._member_completer: MemberCompleter | None = None
#         self.startup_cache = load_cache()

#     @property
#     def current_editor(self) -> CodeEditor:
#         content = self.query_one(ContentSwitcher)
#         active_tab_id = self.active
#         if active_tab_id:
#             try:
#                 tab_pane = content.query_one(f"#{active_tab_id}", TabPane)
#                 return tab_pane.query_one(CodeEditor)
#             except NoMatches:
#                 pass
#         all_editors = content.query(CodeEditor)
#         return all_editors.first(CodeEditor)

#     @property
#     def all_editors(self) -> List[CodeEditor]:
#         try:
#             content = self.query_one(ContentSwitcher)
#             all_editors = content.query(CodeEditor)
#         except NoMatches:
#             return []
#         return list(all_editors)

#     @property
#     def member_completer(self) -> MemberCompleter | None:
#         return self._member_completer

#     @member_completer.setter
#     def member_completer(self, new_completer: MemberCompleter) -> None:
#         self._member_completer = new_completer
#         try:
#             self.current_editor.member_completer = new_completer
#         except NoMatches:
#             pass

#     @property
#     def word_completer(self) -> WordCompleter | None:
#         return self._word_completer

#     @word_completer.setter
#     def word_completer(self, new_completer: WordCompleter) -> None:
#         self._word_completer = new_completer
#         try:
#             self.current_editor.word_completer = new_completer
#         except NoMatches:
#             pass

#     async def on_mount(self) -> None:
#         if self.startup_cache is not None:
#             for _i, buffer in enumerate(self.startup_cache.buffers):
#                 await self.action_new_buffer(state=buffer)
#                 # we can't load the focus state here, since Tabs
#                 # really wants to activate the first tab when it's
#                 # mounted
#         else:
#             await self.action_new_buffer()
#         self.query_one(Tabs).can_focus = False
#         self.current_editor.word_completer = self.word_completer
#         self.current_editor.member_completer = self.member_completer
#         self.remove_class("premount")
#         self.post_message(WidgetMounted(widget=self))

#     def on_focus(self) -> None:
#         self.current_editor.focus()

#     def on_tabbed_content_tab_activated(
#         self, message: TabbedContent.TabActivated
#     ) -> None:
#         message.stop()
#         self.post_message(self.EditorSwitched(active_editor=None))
#         self.current_editor.word_completer = self.word_completer
#         self.current_editor.member_completer = self.member_completer
#         self.current_editor.focus()

#     def watch_theme(self, theme: str) -> None:
#         for editor in self.all_editors:
#             editor.theme = theme

#     async def insert_buffer_with_text(self, query_text: str) -> None:
#         state = BufferState(selection=Selection(), text=query_text)
#         new_editor = await self.action_new_buffer(state=state)
#         new_editor.focus()

#     async def action_new_buffer(
#         self, state: Union[BufferState, None] = None
#     ) -> CodeEditor:
#         self.counter += 1
#         new_tab_id = f"tab-{self.counter}"
#         editor = CodeEditor(
#             id=f"buffer-{self.counter}",
#             text=state.text if state is not None else "",
#             language=self.language,
#             theme=self.theme,
#             word_completer=self.word_completer,
#             member_completer=self.member_completer,
#         )
#         pane = TabPane(
#             f"Tab {self.counter}",
#             editor,
#             id=new_tab_id,
#         )
#         await self.add_pane(pane)
#         if state is not None:
#             editor.selection = state.selection
#         else:
#             self.active = new_tab_id
#             try:
#                 self.current_editor.focus()
#             except NoMatches:
#                 pass
#         if self.counter > 1:
#             self.remove_class("hide-tabs")
#         return editor

#     def action_close_buffer(self) -> None:
#         if self.tab_count > 1:
#             if self.tab_count == 2:
#                 self.add_class("hide-tabs")
#             self.remove_pane(self.active)
#         else:
#             self.current_editor.text = ""
#             self.current_editor.cursor = (0, 0)  # type: ignore
#         self.current_editor.focus()

#     def action_next_buffer(self) -> None:
#         active = self.active
#         if self.tab_count < 2 or active is None:
#             return
#         tabs = self.query(TabPane)
#         next_tabs = tabs[1:]
#         next_tabs.append(tabs[0])
#         lookup = {t.id: nt.id for t, nt in zip(tabs, next_tabs)}
#         self.active = lookup[active]  # type: ignore
#         self.post_message(self.EditorSwitched(active_editor=None))
#         self.current_editor.focus()
#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
from __future__ import annotations

from typing import Union
from textual.widgets import Input
from textual.message import Message
from textual.reactive import reactive

# You'll import your parser later
# from dragonfruit.core.parser import parse_nl_to_sql
from harlequin.nl_to_sql import translate_nl_to_sql



class NlInput(Input):
    """Widget for entering natural language queries."""

    BORDER_TITLE = "Enter your query in English"
    placeholder = "Type a natural language query, then press Enter..."
    theme: reactive[str] = reactive("dragonfruit")

    class QuerySubmitted(Message):
        """Message fired when the user submits a query."""
        def __init__(self, query_text: str, sql_text: Union[str, None] = None) -> None:
            self.query_text = query_text
            self.sql_text = sql_text
            super().__init__()

    def __init__(
        self,
        name: Union[str, None] = None,
        id: Union[str, None] = None,
        classes: Union[str, None] = None,
        disabled: bool = False,
    ):
        super().__init__(
            placeholder=self.placeholder,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    # async def on_input_submitted(self, value: str) -> None:
    #     """Called when Enter is pressed."""
    #     # Later you can hook this into your Lark parser:
    #     # try:
    #     #     sql = parse_nl_to_sql(value)
    #     # except Exception as e:
    #     #     sql = None
    #     #     # Maybe log error somewhere

    #     # For now, just echo back the query
    #     sql = None
    #     await self.post_message(self.QuerySubmitted(query_text=value, sql_text=sql))

    # async def on_input_submitted(self, value: str) -> None:
    #     """Called when Enter is pressed."""
    #     sql = None
    #     try:
    #         sql = translate_nl_to_sql(value)
    #     except Exception as e:
    #         sql = f"-- Error translating: {e}"

    #     # Fire message with both NL and SQL
    #     await self.post_message(self.QuerySubmitted(query_text=value, sql_text=sql))
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """When Enter is pressed in the NL input box."""
        query_text = event.value  # get actual string
        try:
            sql = translate_nl_to_sql(query_text)
        except Exception as e:
            sql = f"-- Error translating: {e}"

        # Post message (no await here!)
        self.post_message(self.QuerySubmitted(query_text, sql))


