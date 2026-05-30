"""Application entry points."""

import os
import sys


def main():
    """Launch the default UI for the current platform."""
    if sys.platform == "android" or os.environ.get("ANDROID_ARGUMENT"):
        from medpulse.ui.android.app import create_app

        create_app().run()
        return

    from medpulse.ui.windows.app import launch

    launch()
