import streamlit as st
# from streamlit_chat import message
#
# message("My message")
# message("Hello bot!", is_user=True)  # align's the message to the right
# message("Other partner message")
# message("How are you bot?", is_user=True)  # align's the message to the right
import uuid
import streamlit as st
import streamlit.components.v1 as components


def mermaid(code: str, height: int = 250, scrolling: bool=True) -> None:
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
st.set_page_config(layout="wide")  # this needs to be the first Streamlit command
st.title("Worst-Case Analysis for Feature Rollouts")

st.markdown("*Check out the [article](https://www.crosstab.io/articles/staged-rollout-analysis) for a detailed walk-through!*")
st.info("test info")
st.markdown("""
## Persistence

There has to be the way to keep `scheduled job` list even between restarts of the `cron` app and fired `job event` has to be executed once it is created.

#### Scheduled job

To store `scheduled job` list there will be SQL storage with `job` table.

```mermaid
erDiagram
    job {
        int id PK
        timestamp created "creation time stamp of job"
        bool is_active "should trigger new event?"
        string url "URL to call"
        string name "optional job name"
        int minute "minute (0 - 59)"
        int hour "hour (0 - 23)"
        int day "day of month (1 - 31)"
        int month "month (1 - 12)"
        int day_of_week "day of week (0 - 6) (Sunday=0 or 7) "
    }
```
""",
            unsafe_allow_html=True,
)

mermaid("""
erDiagram
    job {
        int id PK
        timestamp created "creation time stamp of job"
        bool is_active "should trigger new event?"
        string url "URL to call"
        string name "optional job name"
        int minute "minute (0 - 59)"
        int hour "hour (0 - 23)"
        int day "day of month (1 - 31)"
        int month "month (1 - 12)"
        int day_of_week "day of week (0 - 6) (Sunday=0 or 7) "
    }
""")
