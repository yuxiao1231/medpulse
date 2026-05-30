"""Renderer for LaTeX formulas in Tkinter using matplotlib."""

import matplotlib.mathtext as mathtext
from PIL import Image, ImageTk


def render_formula(latex: str, fontsize: int = 14) -> ImageTk.PhotoImage:
    """Render a LaTeX formula string into a Tkinter PhotoImage."""
    parser = mathtext.MathTextParser("bitmap")
    # to_rgba returns (rgba_array, depth)
    rgba, _ = parser.to_rgba(f"${latex}$", fontsize=fontsize, dpi=120)
    return ImageTk.PhotoImage(Image.fromarray(rgba))
