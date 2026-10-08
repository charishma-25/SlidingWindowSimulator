
def simulate_protocol(total_frames, window_size, protocol, lost_frame=None):
    """
    Simulate Go-Back-N ARQ or Selective Repeat ARQ.
    A selected frame is lost on its first transmission only.
    """

    if total_frames < 1:
        raise ValueError("Total frames must be at least 1.")

    if not 1 <= window_size <= total_frames:
        raise ValueError("Invalid window size.")

    if lost_frame is not None and not 1 <= lost_frame <= total_frames:
        raise ValueError("Lost frame must be within the frame range.")

    if protocol not in ("Go-Back-N", "Selective Repeat"):
        raise ValueError("Unknown protocol.")

    events = []
    attempts = {}
    acknowledged = set()
    lost_once = False
    retransmissions = 0

    def transmit(frame, retransmission=False):
        nonlocal lost_once, retransmissions

        attempts[frame] = attempts.get(frame, 0) + 1

        if retransmission:
            retransmissions += 1
            events.append(f"TIMEOUT: Retransmitting Frame {frame}")

        else:
            events.append(f"SENDER: Transmitting Frame {frame}")

        if frame == lost_frame and not lost_once:
            lost_once = True
            events.append(f"CHANNEL: Frame {frame} was LOST")
            return False

        events.append(f"RECEIVER: Frame {frame} received")

        return True

    base = 1

    while base <= total_frames:
        end = min(base + window_size - 1, total_frames)
        lost_in_window = None

        # Transmit the current sender window.
        for frame in range(base, end + 1):
            received = transmit(frame)

            if received:
                if protocol == "Go-Back-N" and lost_in_window is not None:
                    events.append(
                        f"RECEIVER: Frame {frame} discarded "
                        "(waiting for missing frame)"
                    )
                else:
                    acknowledged.add(frame)
                    events.append(f"RECEIVER: ACK {frame} sent")

            elif lost_in_window is None:
                lost_in_window = frame

        # Recover from the loss.
        if lost_in_window is not None:
            if protocol == "Go-Back-N":
                events.append(
                    f"SENDER: Timeout. Go-Back-N recovery "
                    f"starts from Frame {lost_in_window}"
                )

                for frame in range(lost_in_window, end + 1):
                    transmit(frame, retransmission=True)
                    acknowledged.add(frame)
                    events.append(f"RECEIVER: ACK {frame} sent")

            else:
                events.append(
                    f"SENDER: Selective Repeat recovery "
                    f"for Frame {lost_in_window}"
                )

                # Other correctly received frames remain acknowledged.
                transmit(lost_in_window, retransmission=True)
                acknowledged.add(lost_in_window)
                events.append(
                    f"RECEIVER: ACK {lost_in_window} sent"
                )

        base = end + 1

    total_transmissions = sum(attempts.values())

    frame_status = []
    for frame in range(1, total_frames + 1):
        frame_status.append({
            "Frame": frame,
            "Status": (
                "Delivered"
                if frame in acknowledged
                else "Pending"
            ),
            "Transmission Attempts": attempts.get(frame, 0),
        })

    return {
        "events": events,
        "frames_sent": total_transmissions,
        "frames_delivered": len(acknowledged),
        "retransmissions": retransmissions,
        "frame_status": frame_status,
        "efficiency": (
            total_frames / total_transmissions * 100
            if total_transmissions else 0
        ),
    }
