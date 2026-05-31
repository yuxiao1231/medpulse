"""Renderer for LaTeX formulas in Tkinter using matplotlib."""

import matplotlib.mathtext as mathtext
from PIL import Image, ImageTk


def render_formula(latex, fontsize=14):
    """Render a LaTeX formula string into a Tkinter PhotoImage."""
    parser = mathtext.MathTextParser("bitmap")
    # to_rgba returns (rgba_array, depth)
    rgba, _ = parser.to_rgba("$" + latex + "$", fontsize=fontsize, dpi=120)
    return ImageTk.PhotoImage(Image.fromarray(rgba))
