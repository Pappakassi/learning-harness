"""csvideo: building blocks for narrated computer-science explainer videos in Manim."""
from . import theme
from .scene_base import CSScene, make_text
from .templates import ArrayView, BulletList, Callout, CodePanel, Counter, Pointers

__all__ = ["theme", "CSScene", "make_text", "ArrayView", "Pointers", "CodePanel",
           "BulletList", "Callout", "Counter"]
