import uuid
from itertools import islice
from PIL import Image
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path


def mermaid(code: str, height: int = 250, scrolling: bool = True) -> None:
    new_id = str(uuid.uuid4())
    components.html(
        f"""
        <pre class="mermaid" id="{new_id}">
            {code}
        </pre>

        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true }});
        </script>
        """,
        height=height,
        scrolling=scrolling
    )


class UI:
    """
    Wrap around streamlit UI.
    Remember streamlit acts as singleton so there should be no need to create more than 1 instance of UI.
    """

    # define default memory state here
    DEFAULT_STATE = dict(
        conversations=[],
        user="user",
        active_conversation=[],
        favicon=None,
    )

    def __init__(
            self,
            batch_size: int = 512,
            title: str = "Muninn",
            favicon: str = "./muninn/images/muninn.png"
    ) -> None:
        self.batch_size = max(1, batch_size or 512)
        self.favicon = favicon
        self.title = title
        self.set_state()
        self.show_active_conversation()
        self.prompt = st.session_state.get("prompt")

    def show(self):
        st.set_page_config(
            page_title=self.title,
            layout="centered",
            initial_sidebar_state="expanded",
            page_icon=st.session_state["favicon"],
        )
        st.sidebar.write("### History")
        self.show_active_conversation()
        self.prompt = st.chat_input("Send message", key="prompt", on_submit=self.prompt_callback)

    def prompt_callback(self, *args, **kwargs):
        self.prompt = st.session_state.get("prompt")
        print(f"prompt_call - {self.prompt=} {args=} {kwargs=} st.session_state={st.session_state}")

    def set_state(
            self,
    ) -> None:
        """Fill `streamlit.session_state` with default dict if there is None"""
        if st.session_state.get("has_defaults"):
            return
        # set defaults
        for k, v in self.DEFAULT_STATE.items():
            if k not in st.session_state:
                st.session_state[k] = v

        if self.favicon and Path(self.favicon).exists():
            st.session_state["favicon"] = Image.open(Path(self.favicon), mode="r")
        st.session_state["has_defaults"] = True

    def show_active_conversation(self) -> None:
        """If there is active conversation, shot chat history in main chat window"""
        if not st.session_state["active_conversation"]:
            return
        for message in islice(st.session_state["active_conversation"], 512):
            self.show_message(message["content"], message["type"])

    def show_message(self, text: str, type_: str = None) -> None:
        """Shortcut to show message as system or from one of chat participants"""
        if type_ is None:
            st.write(text)
            return
        st.chat_message(type_).write(text)


def test_main():
    ui = UI()
    ui.show()
    ui.show_message("""
    ### Markdown - Sub Sub Topic
    Here is paragraph for example. 
    ```py
    import os
    ```
    """)


if __name__ == "__main__":
    test_main()
