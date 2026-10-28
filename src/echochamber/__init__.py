"""Temporal Echo Chamber Detection in Online Social Networks.

A reproducible research pipeline for quantifying isolation, embedding homogeneity,
and external exposure scarcity across dynamic communities.
"""

import os
import tempfile

# Set non-interactive and local cache dir for matplotlib
os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "echochamber_mpl"))

__version__ = "0.1.0"
__author__ = "23CSE356 Social Network Analysis Team"
