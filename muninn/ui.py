import uuid

import streamlit as st
import streamlit.components.v1 as components


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
            chat=[],
            user="user",
            title="AI chat",
        )

    def __init__(self):
        self.set_state()
        st.title(st.session_state["title"])
        st.sidebar.title("History")
        self.prompt = st.chat_input(placeholder="Send message", key="prompt", on_submit=self.prompt_call)

    def prompt_call(self, *args, **kwargs):
        print(f"prompt_call - {self.prompt=} {args=} {kwargs=} st.session_state={st.session_state}")

    def set_state(self) -> None:
        """Fill `streamlit.session_state` with default dict if there is None"""
        if st.session_state.get("has_defaults"):
            return
        # set defaults
        for k, v in self.DEFAULT_STATE.items():
            if k not in st.session_state:
                st.session_state[k] = v
        st.session_state["has_defaults"] = True

    def add_message(self, text: str, is_user: bool = False):
        with st.chat_message("ai" if is_user else st.session_state["user"]):
            st.write(text)


def test_main():
    ui = UI()
    if ui.prompt:
        print(f"{ui.prompt=}")


if __name__ == "__main__":
    test_main()
