import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from analytics import comparison_summary, run_comparison, selected_loss_sweep, window_sweep
from protocols import parse_lost_frames, simulate_protocol


class LostFrameInputTests(unittest.TestCase):
    def test_empty_input_means_no_losses(self):
        self.assertEqual(parse_lost_frames("", 8), [])
        self.assertEqual(parse_lost_frames("   ", 8), [])

    def test_single_and_multiple_selected_frames(self):
        self.assertEqual(parse_lost_frames("3", 8), [3])
        self.assertEqual(parse_lost_frames("2, 5, 7", 8), [2, 5, 7])

    def test_duplicates_are_removed(self):
        self.assertEqual(parse_lost_frames("5, 2, 5, 2", 8), [2, 5])

    def test_invalid_and_negative_values_are_rejected(self):
        for value in ("2, abc, 5", "-2", "0", "2,,3", "2.5"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_lost_frames(value, 8)

    def test_frame_greater_than_total_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "outside the configured range"):
            parse_lost_frames("9", 8)


class ProtocolSimulationTests(unittest.TestCase):
    def test_no_loss_delivers_every_frame_without_retries(self):
        for protocol in ("Go-Back-N", "Selective Repeat"):
            result = simulate_protocol(8, 3, protocol)
            self.assertEqual(result["frames_delivered"], 8)
            self.assertEqual(result["frames_sent"], 8)
            self.assertEqual(result["retransmissions"], 0)
            self.assertEqual(result["ack_count"], 8)

    def test_intentionally_lost_frame_retransmission_succeeds(self):
        result = simulate_protocol(8, 4, "Selective Repeat", lost_frames=[2])
        self.assertEqual(result["frames_delivered"], 8)
        self.assertEqual(result["failure_count"], 1)
        self.assertEqual(result["retransmissions"], 1)
        self.assertEqual(result["frame_status"][1]["Transmission Attempts"], 2)

    def test_multiple_losses_are_by_frame_identity_and_recover(self):
        for protocol in ("Go-Back-N", "Selective Repeat"):
            result = simulate_protocol(8, 4, protocol, lost_frames=[2, 5])
            self.assertEqual(result["frames_delivered"], 8)
            self.assertEqual(result["failure_count"], 2)
            self.assertEqual(result["frame_status"][1]["Transmission Attempts"], 2)
            self.assertEqual(result["frame_status"][4]["Transmission Attempts"], 2)

    def test_go_back_n_and_selective_repeat_use_identical_loss_selection(self):
        results = run_comparison(20, 4, [3, 7])
        self.assertEqual(results["Go-Back-N"]["failure_count"], 2)
        self.assertEqual(results["Selective Repeat"]["failure_count"], 2)
        self.assertEqual(results["Go-Back-N"]["frames_delivered"], 20)
        self.assertEqual(results["Selective Repeat"]["frames_delivered"], 20)
        self.assertGreaterEqual(
            results["Go-Back-N"]["retransmissions"],
            results["Selective Repeat"]["retransmissions"],
        )

    def test_success_rate_and_efficiency_use_unique_deliveries_and_attempts(self):
        result = simulate_protocol(4, 4, "Go-Back-N", lost_frames=[2])
        self.assertEqual(result["success_rate"], 100.0)
        self.assertAlmostEqual(result["efficiency"], 4 / 7 * 100)
        self.assertEqual(result["retransmissions"], result["frames_sent"] - 4)

    def test_validates_window_and_lost_frame_range(self):
        with self.assertRaises(ValueError):
            simulate_protocol(5, 6, "Go-Back-N")
        with self.assertRaises(ValueError):
            simulate_protocol(5, 2, "Go-Back-N", lost_frames=[6])


class AnalyticsTests(unittest.TestCase):
    def test_summary_is_data_driven(self):
        results = run_comparison(10, 4, [2])
        self.assertTrue(comparison_summary(results))

    def test_window_and_loss_count_sweeps_are_real_protocol_runs(self):
        windows = window_sweep(5, 3, [2])
        self.assertEqual(len(windows), 6)
        selected_losses = selected_loss_sweep(5, 2, [3, 5])
        self.assertEqual(len(selected_losses), 12)
        count_one = [r for r in selected_losses if r["Number of selected lost frames"] == 1]
        self.assertTrue(all(r["Selected frames"] == "3" for r in count_one))


class StreamlitWorkspaceTests(unittest.TestCase):
    def test_single_comparison_and_analytics_views_run_without_app_errors(self):
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        app = AppTest.from_file(str(app_path), default_timeout=60).run()
        self.assertEqual(len(app.exception), 0)

        app.text_input[0].set_value("3").run()
        app.button[0].click().run()
        self.assertEqual(len(app.exception), 0)

        app.radio[0].set_value("Protocol Comparison").run()
        app.text_input[0].set_value("3, 7").run()
        app.button[0].click().run()
        self.assertEqual(len(app.exception), 0)

        app.radio[0].set_value("Performance Analytics").run()
        app.text_input[0].set_value("3, 7").run()
        app.button[0].click().run()
        self.assertEqual(len(app.exception), 0)


if __name__ == "__main__":
    unittest.main()
