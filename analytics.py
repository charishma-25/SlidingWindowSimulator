"""Reusable deterministic comparison and performance experiment helpers."""

from protocols import PROTOCOLS, simulate_protocol


def run_comparison(total_frames, window_size, lost_frames=None, max_retries=100):
    """Run both real protocol simulations with the same selected frame losses."""
    selected = sorted(set(lost_frames or ()))
    return {
        protocol: simulate_protocol(
            total_frames,
            window_size,
            protocol,
            lost_frames=selected,
            max_retries=max_retries,
        )
        for protocol in PROTOCOLS
    }


def window_sweep(total_frames, max_window, lost_frames=None):
    """Run paired simulations for every valid window size."""
    rows = []
    for window_size in range(1, min(total_frames, max_window) + 1):
        results = run_comparison(total_frames, window_size, lost_frames)
        for protocol, result in results.items():
            rows.append({
                "Window size": window_size,
                "Protocol": protocol,
                "Total transmissions": result["frames_sent"],
                "Retransmissions": result["retransmissions"],
            })
    return rows


def selected_loss_sweep(total_frames, window_size, selected_frames=None):
    """Measure retries as the count of deliberate original-frame losses grows.

    Selected frames are tried first in ascending order; if more points are
    needed, the remaining frame numbers are appended in ascending order.
    Each point runs both protocols from fresh state using the same loss list.
    """
    selected = sorted(set(selected_frames or ()))
    order = selected + [
        frame for frame in range(1, total_frames + 1) if frame not in selected
    ]
    rows = []
    for count in range(total_frames + 1):
        losses = order[:count]
        results = run_comparison(total_frames, window_size, losses)
        for protocol, result in results.items():
            rows.append({
                "Number of selected lost frames": count,
                "Protocol": protocol,
                "Retransmissions": result["retransmissions"],
                "Selected frames": ", ".join(map(str, losses)) or "None",
            })
    return rows


def comparison_summary(results):
    gbn = results["Go-Back-N"]
    sr = results["Selective Repeat"]
    if gbn["frames_sent"] == sr["frames_sent"]:
        if gbn["frames_delivered"] == sr["frames_delivered"]:
            return (
                "Both protocols used the same number of frame transmissions and "
                "delivered the same number of unique frames in this experiment."
            )
        better = "Go-Back-N" if gbn["frames_delivered"] > sr["frames_delivered"] else "Selective Repeat"
        return f"{better} delivered more unique frames with the same number of transmissions in this experiment."
    better = "Go-Back-N" if gbn["frames_sent"] < sr["frames_sent"] else "Selective Repeat"
    more = "Selective Repeat" if better == "Go-Back-N" else "Go-Back-N"
    delivery = (
        " Delivery counts differed, so compare success rates as well."
        if gbn["frames_delivered"] != sr["frames_delivered"]
        else " Both delivered the same number of unique frames."
    )
    return (
        f"{better} used fewer data-frame transmissions ({min(gbn['frames_sent'], sr['frames_sent'])} "
        f"vs {max(gbn['frames_sent'], sr['frames_sent'])}); {more} used more recovery attempts."
        f"{delivery}"
    )
