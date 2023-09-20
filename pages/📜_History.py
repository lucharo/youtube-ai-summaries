import streamlit as st

# from localstorage import *

st.markdown("# History 📜")

history_cache = [] # or load_data('youtube-ai-summaries-history-cache')
# if len(history_cache) > 1:
#     if st.button("Clear local cache 🗑️"):
#         clear_storage()

if 'history' in st.session_state:
    history = st.session_state.history + history_cache
else: 
    history = history_cache

st.write(history_cache)
if len(history) > 0:
    title_options = [entry["title"] for entry in history]
    selected_title = st.selectbox("Select a video:", title_options, index=len(title_options) - 1)
    
    title_entry = None
    for entry in history:
        if entry["title"] == selected_title:
            title_entry = entry
            break

    st.markdown(f'### {entry["title"]}')
    st.markdown(f"**URL:** {entry['url']}")
    with st.expander(f"Expand to see transcript"):
        st.write(entry["transcript"])

    summary_length_options = list(title_entry["summaries"].keys())
    if len(summary_length_options) > 1:
        selected_summary_length = st.selectbox("Select summary length:", summary_length_options, index=0)
        st.markdown(f"**Summary:**")
    else:
        selected_summary_length = summary_length_options[0]
        st.markdown(f"**Summary - {selected_summary_length}:**")

    st.write(entry["summaries"][selected_summary_length]["summary"])
else:
    st.write("No history available.")

with open('pages/sidebar.md', 'r') as sidebar_md:
    st.sidebar.markdown(sidebar_md.read())
