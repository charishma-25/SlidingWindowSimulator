# FrameFlow — Sliding Window Protocol Simulator

FrameFlow is a Streamlit computer-networks project for exploring Go-Back-N and Selective Repeat ARQ. It includes the original single-protocol walkthrough, a paired protocol comparison, and a performance analytics workspace.

## Run locally

From the project directory, create and activate a virtual environment, install dependencies, and start Streamlit:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit. In the existing project environment, run:

```powershell
.\venv\Scripts\python.exe -m streamlit run app.py
```

Choose **Single Simulation**, **Protocol Comparison**, or **Performance Analytics** in the sidebar.

## Deterministic frame loss

Use **Frames to Lose** to enter comma-separated frame numbers whose original transmissions should be lost. For example, with 20 total frames, entering `3, 7` drops the first transmissions of Frames 3 and 7. Leave the field empty for no intentional loss. Duplicate numbers are ignored, and invalid numbers or values outside the configured frame range produce an error.

Selected frame identities are lost on their first original attempt only; their retransmissions succeed. Both protocols receive the same selected loss list. Go-Back-N may also retransmit later unacknowledged frames in the affected window; Selective Repeat retries only the missing frames.

## Metric definitions

- **Delivery success rate:** unique frames successfully delivered ÷ requested frames × 100.
- **Transmission efficiency:** unique frames delivered ÷ total data-frame attempts × 100.
- **Retransmissions:** additional data-frame attempts beyond one original attempt per requested frame.
- **ACK count:** number of ACK events emitted by this simulator's simplified receiver model.
- **Channel failures:** actual dropped data-frame attempts. This can differ from the number of frames selected for loss because a selected frame is lost only once.

The simulator does not model elapsed time, so it does not report throughput. Its analytics charts run actual simulations with the selected frame losses. The lost-frame-count chart starts with the selected frame numbers in ascending order, then adds remaining frame numbers in ascending order, using that same list for each protocol at every point.

## Run checks

```powershell
python -m unittest discover -s tests -v
```
