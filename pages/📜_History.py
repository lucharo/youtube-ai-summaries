import streamlit as st

st.markdown("# History 📜")

history = st.session_state.history
if len(history) > 0:
    history_options = [f"{entry['title']}" for entry in history]
    selected_history_entry = st.selectbox("Select a video:", history_options, index=len(history_options) - 1)
    entry_index = history_options.index(selected_history_entry)
    entry = history[entry_index]

    st.markdown(f'### {entry["title"]}')
    st.markdown(f"**URL:** {entry['url']}")
    with st.expander(f"Expand to see transcript"):
        st.write(entry["transcript"])
    st.markdown(f"**Summary:**")
    st.write(entry["summary"])
else:
    st.write("No history available.")

with open('pages/sidebar.md', 'r') as sidebar_md:
    st.sidebar.markdown(sidebar_md.read())
