from pathlib import Path
from textual.screen import Screen
from textual.widgets import Input, Label, Button
from textual.widgets import TextArea, Header, Footer
from textual.containers import Horizontal, Vertical
from textual.app import App, ComposeResult
from textual.widgets import DirectoryTree

class NoTUI(App):
    """A Note taking terminal application"""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+s", "save", "Save"),
        ("n", "new_note", "New Note"),
        ("ctrl+d", "delete_note", "Delete Note"),
    ]
    CSS_PATH = "NoTUI.tcss"


    def __init__(self):
        super().__init__()
        self.current_file: Path | None = None

    def on_directory_tree_file_selected(self, event:DirectoryTree.FileSelected) -> None:
        path = event.path
        if path.is_file():
            self.current_file = path
            textarea = self.query_one("#editor", TextArea)
            textarea.text = path.read_text()
            last_row = len(textarea.document.lines) - 1
            textarea.cursor_location = (last_row, len(textarea.document.lines[last_row]))

    def action_new_note(self) -> None:
        def handle_name(name: str | None):
            if name:
                path = Path("./Notes") / name
                path.write_text("")
                self.current_file = path
                self.query_one("#editor", TextArea).text = ""
                self.query_one(DirectoryTree).reload()
        self.push_screen(NewNoteScreen(), handle_name)

    def action_delete_note(self) -> None:
        if self.current_file is None:
            self.notify("No note selected", severity="warning")
            return
        def handle_confirm(confirmed: bool):
            if confirmed:
                self.current_file.unlink()
                self.current_file = None
                self.query_one("#editor", TextArea).text = ""
                self.query_one(DirectoryTree).reload()
                self.notify("Note deleted", severity="warning")
        self.push_screen(ConfirmDeleteScreen(),handle_confirm)


    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield DirectoryTree("./Notes/", id="tree")
            yield TextArea(placeholder="Notes go here...", id="editor")
        yield Footer()

    def action_save(self) -> None:
        if self.current_file is None:
            return
        text = self.query_one("#editor", TextArea).text
        self.current_file.write_text(text)
        self.notify("Saved!", severity="success")



class NewNoteScreen(Screen):
    def compose(self):
        with Vertical(id="dialog"):
            yield Label("New note filename:")
            yield Input(placeholder="my-note.txt")
    def on_input_submitted(self, event: Input.Submitted):
        self.dismiss(event.value)

class ConfirmDeleteScreen(Screen):
        def compose(self):
            with Vertical(id="dialog"):
                yield Label("Delete this note?")
                with Horizontal():
                    yield Button("Yes", variant="error", id="yes")
                    yield Button("No", variant="primary", id="no")
        def on_button_pressed(self, event: Button.Pressed):
            self.dismiss(event.button.id == "yes")


if __name__ == "__main__":
    app = NoTUI()
    app.run()
