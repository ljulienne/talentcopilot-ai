# Integration Guide — Release 3.1.1B

Base commit: `528cf3bdabf352cb7bd7a19f5716708e07ab9e7d`

The active Interview Intelligence route remains unchanged, but its implementation now reads the current session through `get_streamlit_session()`.

Validation requirements:

1. Open Interview Intelligence after a real JD/CV analysis.
2. Confirm the candidate names and official fit scores match Candidates and Candidate Intelligence.
3. Confirm the page loads without launching a demo ranking.
4. Click **Generate Interview Strategy** once.
5. Navigate away and back; the questions must be immediately available from session cache.
6. Verify questions refer to the mission, evidence gaps, personal ownership and measurable outcomes.
