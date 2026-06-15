"""Main Streamlit entry point for the Accessible Ebook Reader."""

import streamlit as st

from config.settings import APP_DESCRIPTION, APP_TITLE
from utils.theme import apply_theme, init_theme_state

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_theme_state()
apply_theme()


def main() -> None:
    st.title(f"📖 {APP_TITLE}")
    st.markdown(APP_DESCRIPTION)

    st.markdown("---")
    st.subheader("Get Started")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📚 Library")
        st.markdown(
            "Browse sample books or upload your own XHTML, EPUB, or PDF files."
        )
        if st.button("Go to Library", use_container_width=True, type="primary"):
            st.switch_page("pages/2_Library.py")

    with col2:
        st.markdown("### 📖 Reader")
        st.markdown(
            "Read and listen to your books with text-to-speech, "
            "chapter navigation, and keyboard shortcuts."
        )
        if st.button("Open Reader", use_container_width=True):
            st.switch_page("pages/1_Reader.py")

    with col3:
        st.markdown("### ⚙️ Settings")
        st.markdown(
            "Customize themes, font size, speech speed, and dyslexia-friendly fonts."
        )
        if st.button("Open Settings", use_container_width=True):
            st.switch_page("pages/3_Settings.py")

    st.markdown("---")
    st.subheader("Keyboard Shortcuts")
    st.markdown(
        """
| Key | Action |
|-----|--------|
| `Space` | Play / Pause |
| `Esc` | Stop |
| `→` / `←` | Next / Previous section |
| `H` / `Shift+H` | Next / Previous heading |
| `+` / `-` | Increase / Decrease font size |
| `T` | Cycle theme |
| `B` | Save bookmark |
| `1-9` | Jump to chapter |
        """
    )

    st.info(
        "This app is designed for visually impaired students. "
        "All controls are keyboard-accessible and support high-contrast themes."
    )


if __name__ == "__main__":
    main()
