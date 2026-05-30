import unittest

from medpulse.core.timers.service import countdown_status, elapsed_status


class TimerTests(unittest.TestCase):
    def test_countdown(self):
        state = countdown_status(100, 60, now_epoch=130)
        self.assertEqual(state.elapsed_seconds, 30)
        self.assertEqual(state.remaining_seconds, 30)
        self.assertFalse(state.done)

    def test_elapsed(self):
        state = elapsed_status(100, now_epoch=125)
        self.assertEqual(state.elapsed_seconds, 25)
        self.assertEqual(state.remaining_seconds, 0)


if __name__ == "__main__":
    unittest.main()
