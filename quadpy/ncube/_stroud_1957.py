# -*- coding: utf-8 -*-
#
from __future__ import division

import numpy
import sympy

from ._helpers import _s, NCubeScheme

from ..helpers import untangle, article

_citation = article(
    authors=["A.H. Stroud"],
    title="Remarks on the Disposition of Points in Numerical Integration Formulas",
    journal="Mathematical Tables and Other Aids to Computation",
    volume="11",
    number="60",
    month="oct",
    year="1957",
    pages="257-261",
    url="https://doi.org/10.2307/2001945",
)


def stroud_1957_2(n, symbolic=False):
    sqrt = sympy.sqrt if symbolic else numpy.sqrt

    r = sqrt(3) / 6
    data = [
        (1.0, numpy.array([numpy.full(n, 2 * r)])),
        (+r, _s(n, -1, r)),
        (-r, _s(n, +1, r)),
    ]

    points, weights = untangle(data)
    reference_volume = 2 ** n
    weights *= reference_volume
    return NCubeScheme("Stroud 1957-2", n, weights, points, 2, _citation)


def stroud_1957_3(n, symbolic=False):
    frac = sympy.Rational if symbolic else lambda x, y: x / y
    sqrt = sympy.sqrt if symbolic else numpy.sqrt
    pi = sympy.pi if symbolic else numpy.pi
    sin = sympy.sin if symbolic else numpy.sin
    cos = sympy.cos if symbolic else numpy.cos

    n2 = n // 2 if n % 2 == 0 else (n - 1) // 2
    i_range = range(1, 2 * n + 1)
    pts = [
        [
            [sqrt(frac(2, 3)) * cos((2 * k - 1) * i * pi / n) for i in i_range],
            [sqrt(frac(2, 3)) * sin((2 * k - 1) * i * pi / n) for i in i_range],
        ]
        for k in range(1, n2 + 1)
    ]
    if n % 2 == 1:
        sqrt3pm = numpy.full(2 * n, 1 / sqrt(3))
        sqrt3pm[1::2] *= -1
        pts.append(sqrt3pm)
    pts = numpy.vstack(pts).T

    data = [(frac(1, 2 * n), pts)]

    points, weights = untangle(data)
    reference_volume = 2 ** n
    weights *= reference_volume
    return NCubeScheme("Stroud 1957-3", n, weights, points, 3, _citation)