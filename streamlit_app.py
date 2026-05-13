import streamlit as st
import requests
import time

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="YouTube RAG System",
    page_icon="🎥",
    layout="wide"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = {}
if 'current_video' not in st.session_state:
    st.session_state.current_video = None

# -----------------------------
# API helper functions
# -----------------------------
def ingest_video(youtube_url):
    try:
        response = requests.post(f"{API_BASE_URL}/ingest/", json={"youtube_url": youtube_url}, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def get_job_status(job_id):
    try:
        response = requests.get(f"{API_BASE_URL}/ingest/status/{job_id}", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None

def query_video(video_id, question, top_k=5):
    try:
        response = requests.post(
            f"{API_BASE_URL}/query/",
            json={"video_id": video_id, "question": question, "top_k": top_k},
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error querying video: {str(e)}")
        return None

def list_videos():
    try:
        response = requests.get(f"{API_BASE_URL}/videos/", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching videos: {str(e)}")
        return None

def delete_video(video_id):
    try:
        response = requests.delete(f"{API_BASE_URL}/videos/{video_id}", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error deleting video: {str(e)}")
        return None

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.header("📚 Your Videos")
    if st.button("🔄 Refresh List"):
        st.rerun()

    videos_data = list_videos()
    if videos_data and videos_data['videos']:
        for video in videos_data['videos']:
            with st.expander(f"📹 {video['title'][:50]}..."):
                st.write(f"**Status:** {video['status']}")
                st.write(f"**Chunks:** {video['chunk_count']}")
                st.write(f"**Duration:** {video['duration']}s")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Select", key=f"select_{video['id']}"):
                        st.session_state.current_video = video
                        st.rerun()
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_{video['id']}"):
                        if delete_video(video['id']):
                            st.success("Deleted!")
                            time.sleep(1)
                            st.rerun()
    else:
        st.info("No videos yet. Add one below!")

# -----------------------------
# Main Content
# -----------------------------
st.title("🎥 YouTube RAG System")
st.markdown("Ask questions about YouTube videos using AI")

tab1, tab2 = st.tabs(["💬 Chat", "➕ Add Video"])

# -----------------------------
# Top-level chat input
# -----------------------------
if st.session_state.current_video:
    video_id = st.session_state.current_video['id']
    # Initialize chat history for this video
    if video_id not in st.session_state.messages:
        st.session_state.messages[video_id] = []

    user_question = st.chat_input("Ask a question about this video...")  # Must be top-level

    if user_question:
        # Store user message
        st.session_state.messages[video_id].append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = query_video(video_id, user_question)
                if response:
                    st.markdown(response['answer'])
                    st.session_state.messages[video_id].append({
                        "role": "assistant",
                        "content": response['answer'],
                        "sources": response.get("sources", [])
                    })

# -----------------------------
# Display chat history in tab1
# -----------------------------
with tab1:
    st.header("Chat with Video")
    if st.session_state.current_video:
        video = st.session_state.current_video
        st.success(f"**Current Video:** {video['title']}")

        video_id = video['id']
        for msg in st.session_state.messages.get(video_id, []):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg["role"] == "assistant" and "sources" in msg:
                    with st.expander("📎 Sources"):
                        for i, source in enumerate(msg["sources"], 1):
                            st.write(f"**{i}. Timestamp:** {source['timestamp']}")
                            st.write(f"**Similarity:** {source['similarity_score']:.3f}")
                            st.write(f"*{source['chunk_text']}*")
                            st.divider()

        if st.button("🗑️ Clear Chat"):
            st.session_state.messages[video_id] = []
            st.rerun()
    else:
        st.info("👈 Select a video from the sidebar or add a new one!")

# -----------------------------
# Add Video in tab2
# -----------------------------
with tab2:
    st.header("Add New Video")
    with st.form("add_video_form"):
        youtube_url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
        submitted = st.form_submit_button("🚀 Process Video")

        if submitted and youtube_url:
            result = ingest_video(youtube_url)
            if result:
                job_id = result['job_id']
                video_id = result['video_id']

                if result['status'] == 'completed':
                    st.success("Video already processed! You can query it now.")
                else:
                    st.info(f"Processing started! Job ID: {job_id}")

                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    max_polls = 300
                    for _ in range(max_polls):
                        status = get_job_status(job_id)
                        if status:
                            progress = status['progress']
                            current_step = status['current_step']
                            progress_bar.progress(progress / 100)
                            status_text.text(f"Status: {current_step} ({progress}%)")

                            if status['status'] == 'completed':
                                st.success("✅ Video processed successfully!")
                                time.sleep(2)
                                st.rerun()
                                break
                            elif status['status'] == 'failed':
                                st.error(f"❌ Processing failed: {status.get('error_message', 'Unknown error')}")
                                break

                        time.sleep(1)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown("<div style='text-align: center'><p>Built with ❤️ using FastAPI, Whisper, ChromaDB, and Ollama</p></div>", unsafe_allow_html=True)
