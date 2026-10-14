"""Small, deterministic sliding-window ARQ simulations."""


PROTOCOLS = ("Go-Back-N", "Selective Repeat")


def parse_lost_frames(value, total_frames):
    """Parse comma-separated frame numbers and validate their range."""
    if total_frames < 1:
        raise ValueError("Total frames must be at least 1.")
    value = (value or "").strip()
    if not value:
        return []

    selected = []
    for token in value.split(","):
        token = token.strip()
        if not token.isdigit():
            raise ValueError("Enter positive frame numbers separated by commas, for example: 2, 5, 7.")
        frame = int(token)
        if frame < 1:
            raise ValueError("Frame numbers must be positive integers starting at 1.")
        if frame > total_frames:
            raise ValueError(
                f"Frame {frame} is outside the configured range (1–{total_frames})."
            )
        if frame not in selected:
            selected.append(frame)
    return sorted(selected)


def simulate_protocol(
    total_frames,
    window_size,
    protocol,
    lost_frame=None,
    lost_frames=None,
    failure_plan=None,
    max_retries=100,
):
    """Simulate Go-Back-N or Selective Repeat with optional channel losses.

    ``lost_frame`` preserves the original app API. ``lost_frames`` selects
    frame identities whose original attempt fails once. Retransmissions then
    succeed unless a separate failure plan is provided. Retransmissions count
    additional data-frame attempts beyond one original attempt per frame.
    """
    if total_frames < 1:
        raise ValueError("Total frames must be at least 1.")
    if not 1 <= window_size <= total_frames:
        raise ValueError("Invalid window size.")
    if protocol not in PROTOCOLS:
        raise ValueError("Unknown protocol.")
    if lost_frame is not None and not 1 <= lost_frame <= total_frames:
        raise ValueError("Lost frame must be within the frame range.")
    if max_retries < 0:
        raise ValueError("Maximum retries cannot be negative.")
    selected_losses = set(lost_frames or ())
    if lost_frame is not None:
        selected_losses.add(lost_frame)
    if any(not 1 <= frame <= total_frames for frame in selected_losses):
        raise ValueError("Lost frames must be within the frame range.")
    if failure_plan is not None and selected_losses:
        raise ValueError("Use either selected lost frames or a failure plan, not both.")

    failures = failure_plan or {}
    if selected_losses:
        failures = {frame: {1} for frame in selected_losses}
    for frame, attempts in failures.items():
        if not 1 <= frame <= total_frames:
            raise ValueError("Failure plan contains a frame outside the frame range.")
        if any(attempt < 1 for attempt in attempts):
            raise ValueError("Failure attempt numbers must be positive.")

    events = []
    attempts = {frame: 0 for frame in range(1, total_frames + 1)}
    acknowledged = set()
    failure_count = 0
    max_attempts = max_retries + 1

    def transmit(frame, is_retry=False):
        nonlocal failure_count
        attempts[frame] += 1
        attempt_number = attempts[frame]
        if is_retry:
            events.append(f"TIMEOUT: Retransmitting Frame {frame}")
        else:
            events.append(f"SENDER: Transmitting Frame {frame}")
        if attempt_number in failures.get(frame, ()):
            failure_count += 1
            events.append(f"CHANNEL: Frame {frame} was LOST")
            return False
        events.append(f"RECEIVER: Frame {frame} received")
        return True

    for start in range(1, total_frames + 1, window_size):
        end = min(start + window_size - 1, total_frames)
        # Initial transmissions are sent for the full window.
        gap_seen = False
        for frame in range(start, end + 1):
            received = transmit(frame)
            if not received:
                gap_seen = True
            elif protocol == "Go-Back-N" and gap_seen:
                events.append(
                    f"RECEIVER: Frame {frame} discarded (waiting for missing frame)"
                )
            else:
                acknowledged.add(frame)
                events.append(f"RECEIVER: ACK {frame} sent")

        if protocol == "Go-Back-N":
            while any(frame not in acknowledged for frame in range(start, end + 1)):
                first_missing = next(
                    frame for frame in range(start, end + 1)
                    if frame not in acknowledged
                )
                events.append(
                    f"SENDER: Timeout. Go-Back-N recovery starts from Frame {first_missing}"
                )
                gap_seen = False
                for frame in range(first_missing, end + 1):
                    if frame in acknowledged:
                        continue
                    if attempts[frame] >= max_attempts:
                        continue
                    received = transmit(frame, is_retry=True)
                    if not received:
                        gap_seen = True
                    elif gap_seen:
                        events.append(
                            f"RECEIVER: Frame {frame} discarded (waiting for missing frame)"
                        )
                    else:
                        acknowledged.add(frame)
                        events.append(f"RECEIVER: ACK {frame} sent")
                if all(attempts[frame] >= max_attempts or frame in acknowledged
                       for frame in range(start, end + 1)):
                    break
        else:
            for frame in range(start, end + 1):
                while frame not in acknowledged and attempts[frame] < max_attempts:
                    events.append(f"SENDER: Selective Repeat recovery for Frame {frame}")
                    if transmit(frame, is_retry=True):
                        acknowledged.add(frame)
                        events.append(f"RECEIVER: ACK {frame} sent")

    total_transmissions = sum(attempts.values())
    delivered = len(acknowledged)
    retransmissions = total_transmissions - total_frames
    frame_status = [
        {
            "Frame": frame,
            "Status": "Delivered" if frame in acknowledged else "Pending",
            "Transmission Attempts": attempts[frame],
        }
        for frame in range(1, total_frames + 1)
    ]
    return {
        "events": events,
        "frames_sent": total_transmissions,
        "original_transmissions": total_frames,
        "frames_delivered": delivered,
        "retransmissions": retransmissions,
        "ack_count": sum("RECEIVER: ACK" in event for event in events),
        "failure_count": failure_count,
        "frame_status": frame_status,
        "success_rate": delivered / total_frames * 100,
        "efficiency": delivered / total_transmissions * 100 if total_transmissions else 0,
        "retransmission_overhead": (
            retransmissions / total_transmissions * 100 if total_transmissions else 0
        ),
    }
