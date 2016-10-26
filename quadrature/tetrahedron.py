# -*- coding: utf-8 -*-
#
import math
import numpy
import sympy

from . import helpers


def show(tet, scheme):
    '''Shows the quadrature points on a given tetrahedron. The size of the
    balls around the points coincides with their weights.
    '''
    from matplotlib import pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.set_aspect('equal')

    edges = numpy.array([
        [tet[0], tet[1]],
        [tet[0], tet[2]],
        [tet[0], tet[3]],
        [tet[1], tet[2]],
        [tet[1], tet[3]],
        [tet[2], tet[3]],
        ])
    for edge in edges:
        plt.plot(edge[:, 0], edge[:, 1], edge[:, 2], '-k')

    transformed_pts = \
        + numpy.outer(
            (1.0 - scheme.points[:, 0]
                 - scheme.points[:, 1]
                 - scheme.points[:, 2]),
            tet[0]
            ) \
        + numpy.outer(scheme.points[:, 0], tet[1]) \
        + numpy.outer(scheme.points[:, 1], tet[2]) \
        + numpy.outer(scheme.points[:, 2], tet[3])

    vol = integrate(lambda x: numpy.ones(1), tet, Keast(0))
    helpers.plot_balls(
        plt, ax, transformed_pts, scheme.weights, vol,
        tet[:, 0].min(), tet[:, 0].max(),
        tet[:, 1].min(), tet[:, 1].max(),
        tet[:, 2].min(), tet[:, 2].max(),
        )
    return


def integrate(f, tetrahedron, scheme):
    xi = scheme.points.T
    x = \
        + numpy.outer(tetrahedron[0], 1.0 - xi[0] - xi[1] - xi[2]) \
        + numpy.outer(tetrahedron[1], xi[0]) \
        + numpy.outer(tetrahedron[2], xi[1]) \
        + numpy.outer(tetrahedron[3], xi[2])

    # det is the signed volume of the tetrahedron
    J0 = \
        - numpy.outer(tetrahedron[0], 1.0) \
        + numpy.outer(tetrahedron[1], 1.0)
    J1 = \
        - numpy.outer(tetrahedron[0], 1.0) \
        + numpy.outer(tetrahedron[2], 1.0)
    J2 = \
        - numpy.outer(tetrahedron[0], 1.0) \
        + numpy.outer(tetrahedron[3], 1.0)
    det = J0[0]*J1[1]*J2[2] + J1[0]*J2[1]*J0[2] + J2[0]*J0[1]*J1[2] \
        - J0[2]*J1[1]*J2[0] - J1[2]*J2[1]*J0[0] - J2[2]*J0[1]*J1[0]
    # reference volume
    det *= 1.0/6.0

    return math.fsum(scheme.weights * f(x).T * abs(det))


def _s4():
    return numpy.array([
        [0.25, 0.25, 0.25, 0.25]
        ])


def _s31(a):
    b = 1.0 - 3*a
    return numpy.array([
        [a, a, a, b],
        [a, a, b, a],
        [a, b, a, a],
        [b, a, a, a],
        ])


def _s22(a):
    b = 0.5 - a
    return numpy.array([
        [a, a, b, b],
        [a, b, a, b],
        [b, a, a, b],
        [a, b, b, a],
        [b, a, b, a],
        [b, b, a, a],
        ])


def _s211(a, b):
    c = 1.0 - 2*a - b
    return numpy.array([
        [a, a, b, c],
        [a, b, a, c],
        [b, a, a, c],
        [a, b, c, a],
        [b, a, c, a],
        [b, c, a, a],
        [a, a, c, b],
        [a, c, a, b],
        [c, a, a, b],
        [a, c, b, a],
        [c, a, b, a],
        [c, b, a, a],
        ])


def _s1111(a, b, c):
    d = 1.0 - a - b - c
    return numpy.array([
        [a, b, c, d],
        [a, b, d, c],
        [a, c, b, d],
        [a, c, d, b],
        [a, d, b, c],
        [a, d, c, b],
        [b, a, c, d],
        [b, a, d, c],
        [b, c, a, d],
        [b, c, d, a],
        [b, d, a, c],
        [b, d, c, a],
        [c, a, b, d],
        [c, a, d, b],
        [c, b, a, d],
        [c, b, d, a],
        [c, d, a, b],
        [c, d, b, a],
        [d, a, b, c],
        [d, a, c, b],
        [d, b, a, c],
        [d, b, c, a],
        [d, c, a, b],
        [d, c, b, a],
        ])


class HammerMarloweStroud(object):
    '''
    P.C. Hammer, O.J. Marlowe and A.H. Stroud,
    Numerical Integration Over Simplexes and Cones,
    Mathematical Tables and Other Aids to Computation,
    Vol. 10, No. 55, Jul. 1956, pp. 130-137,
    <https://doi.org/10.1090/S0025-5718-1956-0086389-6>.

    Abstract:
    In this paper we develop numerical integration formulas for simplexes and
    cones in n-space for n>=2. While several papers have been written on
    numerical integration in higher spaces, most of these have dealt with
    hyperrectangular regions. For certain exceptions see [3]. Hammer and Wymore
    [1] have given a first general type theory designed through systematic use
    of cartesian product regions and affine transformations to extend the
    possible usefulness of formulas for each region.

    Two of the schemes also appear in

    P.C. Hammer, Arthur H. Stroud,
    Numerical Evaluation of Multiple Integrals II,
    Mathematical Tables and Other Aids to Computation.
    Vol. 12, No. 64 (Oct., 1958), pp. 272-280,
    <http://www.jstor.org/stable/2002370>
    '''
    def __init__(self, index):
        if index == 1:
            self.weights = numpy.concatenate([
                0.25 * numpy.ones(4),
                ])
            bary = numpy.concatenate([
                self._r(1.0 / numpy.sqrt(5.0)),
                ])
            self.degree = 2
        elif index == 2:
            self.weights = numpy.concatenate([
                0.25 * numpy.ones(4),
                ])
            bary = numpy.concatenate([
                self._r(-1.0 / numpy.sqrt(5.0)),
                ])
            self.degree = 2
        elif index == 3:
            self.weights = numpy.concatenate([
                -0.8 * numpy.ones(1),
                9.0/20.0 * numpy.ones(4),
                ])
            bary = numpy.concatenate([
                _s4(),
                self._r(1.0 / 3.0),
                ])
            self.degree = 3
        else:
            raise ValueError('Illegal Hammer-Marlowe-Stroud index')

        self.points = bary[:, 1:]
        return

    def _r(self, r):
        '''Given $r$ (as appearing in the article), it returns the barycentric
        coordinates of the three points.
        '''
        a = r + (1.0-r) / 4.0
        b = (1.0 - a) / 3.0
        return numpy.array([
            [a, b, b, b],
            [b, a, b, b],
            [b, b, a, b],
            [b, b, b, a],
            ])


def _newton_cotes(n, point_fun):
    '''
    Construction after

    P. Silvester,
    Symmetric quadrature formulae for simplexes
    Math. Comp., 24, 95-100 (1970),
    <https://doi.org/10.1090/S0025-5718-1970-0258283-6>.
    '''
    degree = n

    # points
    idx = numpy.array([
        [i, j, k, n-i-j-k]
        for i in range(n + 1)
        for j in range(n + 1 - i)
        for k in range(n + 1 - i - j)
        ])
    bary = point_fun(idx, n)
    points = bary[:, [1, 2, 3]]

    # weights
    if n == 0:
        weights = numpy.ones(1)
        return points, weights, degree

    def get_poly(t, m, n):
        return sympy.prod([
            sympy.poly(
                (t - point_fun(k, n)) / (point_fun(m, n) - point_fun(k, n))
            )
            for k in range(m)
            ])
    weights = numpy.empty(len(points))
    idx = 0
    for i in range(n + 1):
        for j in range(n + 1 - i):
            for k in range(n + 1 - i - j):
                l = n - i - j - k
                # Compute weight.
                # Define the polynomial which to integrate over the
                # tetrahedron.
                t = sympy.DeferredVector('t')
                g = get_poly(t[0], i, n) \
                    * get_poly(t[1], j, n) \
                    * get_poly(t[2], k, n) \
                    * get_poly(t[3], l, n)
                # The integral of monomials over a tetrahedron are well-known,
                # see Silvester.
                weights[idx] = numpy.sum([
                     c * numpy.prod([math.factorial(k) for k in m]) * 6.0
                     / math.factorial(numpy.sum(m) + 3)
                     for m, c in zip(g.monoms(), g.coeffs())
                     ])
                idx += 1
    return points, weights, degree


class NewtonCotesClosed(object):
    def __init__(self, n):
        self.points, self.weights, self.degree = \
            _newton_cotes(n, lambda k, n: k / float(n))
        return


class NewtonCotesOpen(object):
    def __init__(self, n):
        self.points, self.weights, self.degree = \
            _newton_cotes(n, lambda k, n: (k+1) / float(n+4))
        return


class Yu(object):
    '''
    Yu Jinyun,
    Symmetyric Gaussian quadrature formulae for tetrahedronal regions,
    Computer Methods in Applied Mechanics and Engineering, 43 (1984) 349-353,
    <https://dx.doi.org/10.1016/0045-7825(84)90072-0>.

    Abstract:
    Quadrature formulae of degrees 2 to 6 are presented for the numerical
    integration of a function over tetrahedronal regions. The formulae
    presented are of Gaussian type and fully symmetric with respect to the four
    vertices of the tetrahedron.
    '''
    def __init__(self, index):
        if index == 1:
            self.weights = 0.25 * numpy.ones(4)
            bary = _s31(0.138196601125015)
            self.degree = 2
        elif index == 2:
            self.weights = numpy.concatenate([
                -0.8 * numpy.ones(1),
                0.45 * numpy.ones(4)
                ])
            bary = numpy.concatenate([
                _s4(),
                _s31(1.0/6.0)
                ])
            self.degree = 3
        elif index == 3:
            self.weights = numpy.concatenate([
                0.5037379410012282E-01 * numpy.ones(4),
                0.6654206863329239E-01 * numpy.ones(12)
                ])
            bary = numpy.concatenate([
                _s31(0.7611903264425430E-01),
                _s211(0.4042339134672644, 0.1197005277978019)
                ])
            self.degree = 4
        elif index == 4:
            self.weights = numpy.concatenate([
                0.1884185567365411 * numpy.ones(1),
                0.6703858372604275E-01 * numpy.ones(4),
                0.4528559236327399E-01 * numpy.ones(12)
                ])
            bary = numpy.concatenate([
                _s4(),
                _s31(0.8945436401412733E-01),
                _s211(0.4214394310662522, 0.1325810999384657),
                ])
            self.degree = 5
        elif index == 5:
            self.weights = numpy.concatenate([
                0.9040129046014750E-01 * numpy.ones(1),
                0.1911983427899124E-01 * numpy.ones(4),
                0.4361493840666568E-01 * numpy.ones(12),
                0.2581167596199161E-01 * numpy.ones(12)
                ])
            bary = numpy.concatenate([
                _s4(),
                _s31(0.5742691731735682E-01),
                _s211(0.2312985436519147, 0.5135188412556341E-01),
                _s211(0.4756909881472290E-01, 0.2967538129690260),
                ])
            self.degree = 6
        else:
            raise ValueError('Illegal closed Yu index')

        self.points = bary[:, [1, 2, 3]]
        return


class Keast(object):
    '''
    P. Keast,
    Moderate degree tetrahedral quadrature formulas,
    CMAME 55: 339-348
    1986,
    <http://dx.doi.org/10.1016/0045-7825(86)90059-9>.

    Abstract:
    Quadrature formulas of degrees 4 to 8 for numerical integration over the
    tetrahedron are constructed. The formulas are fully symmetric with respect
    to the tetrahedron, and in some cases are the minimum point rules with this
    symmetry.

    https://people.sc.fsu.edu/~jburkardt/datasets/quadrature_rules_tet/quadrature_rules_tet.html
    '''
    def __init__(self, index):
        if index == 0:
            # Does no appear in Keast's article.
            self.weights = numpy.array([
                1.0
                ])
            bary = _s4()
            self.degree = 1
        elif index == 1:
            # Does no appear in Keast's article.
            self.weights = 0.25 * numpy.ones(4)
            bary = _s31(0.1381966011250105)
            self.degree = 2
        elif index == 2:
            # Does no appear in Keast's article.
            self.weights = numpy.concatenate([
                -0.8 * numpy.ones(1),
                0.45 * numpy.ones(4),
                ])
            bary = numpy.concatenate([
                _s4(),
                _s31(1.0/6.0),
                ])
            self.degree = 3
        elif index == 3:
            # Does no appear in Keast's article.
            self.weights = numpy.concatenate([
                0.2177650698804054 * numpy.ones(4),
                0.0214899534130631 * numpy.ones(6),
                ])
            bary = numpy.concatenate([
                _s31(0.1438564719343852),
                _s22(0.5),
                ])
            self.degree = 3
        elif index == 4:
            self.weights = numpy.concatenate([
                -148.0 / 1875.0 * numpy.ones(1),
                343.0 / 7500.0 * numpy.ones(4),
                56.0 / 375.0 * numpy.ones(6),
                ])
            bary = numpy.concatenate([
                _s4(),
                _s31(1.0/14.0),
                _s22(0.3994035761667992),
                ])
            self.degree = 4
        elif index == 5:
            self.weights = numpy.concatenate([
                2.0/105.0 * numpy.ones(6),
                0.0885898247429807 * numpy.ones(4),
                0.1328387466855907 * numpy.ones(4),
                ])
            bary = numpy.concatenate([
                _s22(0.5),
                _s31(0.1005267652252045),
                _s31(0.3143728734931922),
                ])
            self.degree = 4
        elif index == 6:
            self.weights = numpy.concatenate([
                6544.0 / 36015.0 * numpy.ones(1),
                81.0 / 2240.0 * numpy.ones(4),
                161051.0 / 2304960.0 * numpy.ones(4),
                338.0 / 5145.0 * numpy.ones(6),
                ])
            bary = numpy.concatenate([
                _s4(),
                _s31(1.0/3.0),
                _s31(1.0/11.0),
                _s22(0.0665501535736643),
                ])
            self.degree = 5
        elif index == 7:
            self.weights = numpy.concatenate([
                0.0399227502581679 * numpy.ones(4),
                0.0100772110553207 * numpy.ones(4),
                0.0553571815436544 * numpy.ones(4),
                27.0/560.0 * numpy.ones(12),
                ])
            bary = numpy.concatenate([
                _s31(0.2146028712591517),
                _s31(0.0406739585346113),
                _s31(0.3223378901422757),
                _s211(0.0636610018750175, 0.2696723314583159)
                ])
            self.degree = 6
        elif index == 8:
            self.weights = numpy.concatenate([
                0.1095853407966528 * numpy.ones(1),
                0.0635996491464850 * numpy.ones(4),
                -0.3751064406859797 * numpy.ones(4),
                0.0293485515784412 * numpy.ones(4),
                0.0058201058201058 * numpy.ones(6),
                0.1653439153439105 * numpy.ones(12),
                ])
            bary = numpy.concatenate([
                _s4(),
                _s31(0.0782131923303186),
                _s31(0.1218432166639044),
                _s31(0.3325391644464206),
                _s22(0.5),
                _s211(0.1, 0.2),
                ])
            self.degree = 7
        elif index == 9:
            self.weights = numpy.concatenate([
                -0.2359620398477557 * numpy.ones(1),
                0.0244878963560562 * numpy.ones(4),
                0.0039485206398261 * numpy.ones(4),
                0.0263055529507371 * numpy.ones(6),
                0.0829803830550589 * numpy.ones(6),
                0.0254426245481023 * numpy.ones(12),
                0.0134324384376852 * numpy.ones(12),
                ])
            bary = numpy.concatenate([
                _s4(),
                _s31(0.1274709365666390),
                _s31(0.0320788303926323),
                _s22(0.0497770956432810),
                _s22(0.1837304473985499),
                _s211(0.2319010893971509, 0.5132800333608811),
                _s211(0.0379700484718286, 0.1937464752488044),
                ])
            self.degree = 7
        elif index == 10:
            self.weights = 6 * numpy.concatenate([
                # Note: In Keast's article, the first weight is incorrectly
                # given with a positive sign.
                -0.393270066412926145e-01 * numpy.ones(1),
                +0.408131605934270525e-02 * numpy.ones(4),
                +0.658086773304341943e-03 * numpy.ones(4),
                +0.438425882512284693e-02 * numpy.ones(6),
                +0.138300638425098166e-01 * numpy.ones(6),
                +0.424043742468372453e-02 * numpy.ones(12),
                +0.223873973961420164e-02 * numpy.ones(12),
                ])
            bary = numpy.concatenate([
                _s4(),
                _s31(0.127470936566639015e-00),
                _s31(0.320788303926322960e-01),
                _s22(0.497770956432810185e-01),
                _s22(0.183730447398549945e-00),
                _s211(0.231901089397150906e-00, 0.229177878448171174e-01),
                _s211(0.379700484718286102e-01, 0.730313427807538396e-00),
                ])
            self.degree = 8
        else:
            raise ValueError('Illegal Keast index')

        self.points = bary[:, 1:]
        return


class LiuVinokur(object):
    '''
    Y. Liu and M. Vinokur,
    Exact Integrations of Polynomials and Symmetric Quadrature Formulas over
    Arbitrary Polyhedral Grids,
    Journal of Computational Physics, 140, 122–147 (1998).
    DOI: 10.1006/jcph.1998.5884,
    <http://dx.doi.org/10.1006/jcph.1998.5884>.
    '''
    def __init__(self, index):
        if index == 1:
            self.weights = numpy.concatenate([
                1.0 * numpy.ones(1),
                ])
            bary = numpy.concatenate([
                _s4(),
                ])
            self.degree = 1
        elif index == 2:
            self.weights = numpy.concatenate([
                0.25 * numpy.ones(4),
                ])
            bary = numpy.concatenate([
                self._r_alpha(1.0),
                ])
            self.degree = 1
        elif index == 3:
            self.weights = numpy.concatenate([
                0.25 * numpy.ones(4),
                ])
            bary = numpy.concatenate([
                self._r_alpha(1.0 / numpy.sqrt(5.0)),
                ])
            self.degree = 2
        elif index == 4:
            self.weights = numpy.concatenate([
                0.8 * numpy.ones(1),
                0.05 * numpy.ones(4),
                ])
            bary = numpy.concatenate([
                _s4(),
                self._r_alpha(1.0),
                ])
            self.degree = 2
        elif index == 5:
            self.weights = numpy.concatenate([
                -0.8 * numpy.ones(1),
                0.45 * numpy.ones(4),
                ])
            bary = numpy.concatenate([
                _s4(),
                self._r_alpha(1.0/3.0),
                ])
            self.degree = 3
        elif index == 6:
            self.weights = numpy.concatenate([
                1.0/40.0 * numpy.ones(4),
                9.0/40.0 * numpy.ones(4),
                ])
            bary = numpy.concatenate([
                self._r_alpha(1.0),
                self._r_alpha(-1.0/3.0),
                ])
            self.degree = 3
        elif index == 7:
            self.weights = numpy.concatenate([
                -148.0/1875.0 * numpy.ones(1),
                343.0/7500.0 * numpy.ones(4),
                56.0/375.0 * numpy.ones(6),
                ])
            bary = numpy.concatenate([
                _s4(),
                self._r_alpha(5.0/7.0),
                self._r_beta(numpy.sqrt(70.0)/28.0),
                ])
            self.degree = 4
        elif index == 8:
            alpha1 = (
                + numpy.sqrt(65944.0 - 19446*numpy.sqrt(11))
                + 51*numpy.sqrt(11) - 154.0
                ) / 89.0
            alpha2 = (
                - numpy.sqrt(65944.0 - 19446*numpy.sqrt(11))
                + 51*numpy.sqrt(11) - 154.0
                ) / 89.0
            self.weights = numpy.concatenate([
                (17*alpha2 - 7.0)/(420.0*alpha1**2 * (alpha2 - alpha1))
                * numpy.ones(4),
                (17*alpha1 - 7.0)/(420.0*alpha2**2 * (alpha1 - alpha2))
                * numpy.ones(4),
                2.0/105.0 * numpy.ones(6),
                ])
            bary = numpy.concatenate([
                self._r_alpha(alpha1),
                self._r_alpha(alpha2),
                self._r_beta(0.5),
                ])
            self.degree = 4
        elif index == 9:
            self.weights = numpy.concatenate([
                -32.0/15.0 * numpy.ones(1),
                3.0/280.0 * numpy.ones(4),
                125.0/168.0 * numpy.ones(4),
                2.0/105.0 * numpy.ones(6),
                ])
            bary = numpy.concatenate([
                _s4(),
                self._r_alpha(1),
                self._r_alpha(0.2),
                self._r_beta(0.5),
                ])
            self.degree = 4
        elif index == 10:
            self.weights = numpy.concatenate([
                32.0/105.0 * numpy.ones(1),
                -31.0/840.0 * numpy.ones(4),
                27.0/280.0 * numpy.ones(4),
                4.0/105.0 * numpy.ones(12),
                ])
            bary = numpy.concatenate([
                _s4(),
                self._r_alpha(1),
                self._r_alpha(-1.0/3.0),
                self._r_gamma_delta(
                    (2 + numpy.sqrt(2.0)) / 4.0,
                    (2 - numpy.sqrt(2.0)) / 4.0,
                    ),
                ])
            self.degree = 4
        elif index == 11:
            self.weights = numpy.concatenate([
                (11.0 - 4*numpy.sqrt(2.0)) / 840.0 * numpy.ones(4),
                (243.0 - 108*numpy.sqrt(2.0)) / 1960.0 * numpy.ones(4),
                (62.0 + 44*numpy.sqrt(2.0)) / 735.0 * numpy.ones(4),
                2.0/105.0 * numpy.ones(6),
                ])
            bary = numpy.concatenate([
                self._r_alpha(1),
                self._r_alpha(-1.0/3.0),
                self._r_alpha(numpy.sqrt(2.0) - 1.0),
                self._r_beta(0.5),
                ])
            self.degree = 4
        elif index == 12:
            lmbda = 4.0/27.0 * (4.0 * numpy.sqrt(79.0)*numpy.cos(
                (numpy.arccos(67*numpy.sqrt(79.0)/24964.0) + 2*numpy.pi) / 3.0
                ) + 71.0
                )
            alpha1 = (
                + numpy.sqrt(9*lmbda**2 - 248*lmbda + 1680) + 28.0 - 3*lmbda
                ) / (112.0 - 10*lmbda)
            alpha2 = (
                - numpy.sqrt(9*lmbda**2 - 248*lmbda + 1680) + 28.0 - 3*lmbda
                ) / (112.0 - 10*lmbda)
            w1 = ((21.0 - lmbda)*alpha2 - 7.0) \
                / (420.0*alpha1**2 * (alpha2 - alpha1))
            w2 = ((21.0 - lmbda)*alpha1 - 7.0) \
                / (420.0*alpha2**2 * (alpha1 - alpha2))
            self.weights = numpy.concatenate([
                w1 * numpy.ones(4),
                w2 * numpy.ones(4),
                lmbda**2/840.0 * numpy.ones(6),
                ])
            bary = numpy.concatenate([
                self._r_alpha(alpha1),
                self._r_alpha(alpha2),
                self._r_beta(1.0 / numpy.sqrt(lmbda)),
                ])
            self.degree = 5
        elif index == 13:
            self.weights = numpy.concatenate([
                -16.0/21.0 * numpy.ones(1),
                (2249.0 - 391.0*numpy.sqrt(13.0)) / 10920.0 * numpy.ones(4),
                (2249.0 + 391.0*numpy.sqrt(13.0)) / 10920.0 * numpy.ones(4),
                2.0 / 105.0 * numpy.ones(6),
                ])
            bary = numpy.concatenate([
                _s4(),
                self._r_alpha((2.0 + numpy.sqrt(13.0)) / 9.0),
                self._r_alpha((2.0 - numpy.sqrt(13.0)) / 9.0),
                self._r_beta(0.5),
                ])
            self.degree = 5
        elif index == 14:
            self.weights = numpy.concatenate([
                16.0/105.0 * numpy.ones(1),
                1.0/280.0 * numpy.ones(4),
                81.0/1400.0 * numpy.ones(4),
                64.0/525.0 * numpy.ones(4),
                2.0/105.0 * numpy.ones(6),
                ])
            bary = numpy.concatenate([
                _s4(),
                self._r_alpha(1.0),
                self._r_alpha(-1.0/3.0),
                self._r_alpha(0.5),
                self._r_beta(0.5),
                ])
            self.degree = 5
        else:
            raise ValueError('Illegal Liu-Vinokur index')

        self.points = bary[:, 1:]
        return

    def _r_alpha(self, alpha):
        '''From the article:

        mu_i = (1 + (n-1) alpha) / n,
        mu_j = (1 - alpha) / n    for j!=i,

        where n is the number of vertices
        '''
        a = (1.0 + 3*alpha) / 4.0
        b = (1.0 - alpha) / 4.0
        return numpy.array([
            [a, b, b, b],
            [b, a, b, b],
            [b, b, a, b],
            [b, b, b, a],
            ])

    def _r_beta(self, beta):
        '''From the article:

        mu_i = (1+(n-2)*beta) / n,
        mu_j = mu_i,
        mu_k = (1 - 2*beta) / n    for k!=i, k!=j,

        where n is the number of vertices.
        '''
        a = (1.0 + 2*beta) / 4.0
        b = (1.0 - 2*beta) / 4.0
        return numpy.array([
            [a, a, b, b],
            [a, b, a, b],
            [b, a, a, b],
            [a, b, b, a],
            [b, a, b, a],
            [b, b, a, a],
            ])

    def _r_gamma_delta(self, gamma, delta):
        '''From the article:

        mu_i = (1 + (n-1) gamma - delta) / n,
        mu_j = (1 + (n-1) delta - gamma) / n,
        mu_k = (1 - gamma - delta) / n    for k!=i, k!=j,

        where n is the number of vertices
        '''
        b = (1.0 + 3*gamma - delta) / 4.0
        c = (1.0 + 3*delta - gamma) / 4.0
        a = (1.0 - gamma - delta) / 4.0
        return numpy.array([
            [a, a, b, c],
            [a, b, a, c],
            [b, a, a, c],
            [a, b, c, a],
            [b, a, c, a],
            [b, c, a, a],
            [a, a, c, b],
            [a, c, a, b],
            [c, a, a, b],
            [a, c, b, a],
            [c, a, b, a],
            [c, b, a, a],
            ])


class Zienkiewicz(object):
    '''
    Olgierd Zienkiewicz,
    The Finite Element Method,
    Sixth Edition,
    Butterworth-Heinemann, 2005,
    ISBN: 0750663200,
    <http://www.sciencedirect.com/science/book/9780750664318>,
    <https://people.sc.fsu.edu/~jburkardt/datasets/quadrature_rules_tet/quadrature_rules_tet.html>.
    '''
    def __init__(self, index):
        if index == 4:
            self.weights = 0.25 * numpy.ones(4)
            bary = _s31(0.1381966011250105)
            self.degree = 2
        elif index == 5:
            self.weights = numpy.concatenate([
                -0.8 * numpy.ones(1),
                0.45 * numpy.ones(4),
                ])
            bary = numpy.concatenate([
                _s4(),
                _s31(1.0/6.0),
                ])
            self.degree = 3
        else:
            raise ValueError('Illegal closed Newton-Cotes index')

        self.points = bary[:, [1, 2, 3]]
        return


class ZhangCuiLiu(object):
    '''
    Linbo Zhang, Tao Cui and Hui Liu,
    A set of symmetric quadrature rules on triangles and tetrahedra,
    Journal of Computational Mathematics
    Vol. 27, No. 1 (January 2009), pp. 89-96,
    <http://www.jstor.org/stable/43693493>.

    Abstract:
    We present a program for computing symmetric quadrature rules on triangles
    and tetrahedra. A set of rules are obtained by using this program.
    Quadrature rules up to order 21 on triangles and up to order 14 on
    tetrahedra have been obtained which are useful for use in finite element
    computations. All rules presented here have positive weights with points
    lying within the integration domain.
    '''
    def __init__(self, index):
        if index == 1:
            self.weights = numpy.concatenate([
                0.0063971477799023213214514203351730 * numpy.ones(4),
                0.0401904480209661724881611584798178 * numpy.ones(4),
                0.0243079755047703211748691087719226 * numpy.ones(4),
                0.0548588924136974404669241239903914 * numpy.ones(4),
                0.0357196122340991824649509689966176 * numpy.ones(6),
                0.0071831906978525394094511052198038 * numpy.ones(12),
                0.0163721819453191175409381397561191 * numpy.ones(12),
                ])
            bary = numpy.concatenate([
                _s31(.0396754230703899012650713295393895),
                _s31(.3144878006980963137841605626971483),
                _s31(.1019866930627033000000000000000000),
                _s31(.1842036969491915122759464173489092),
                _s22(.0634362877545398924051412387018983),
                _s211(
                    .0216901620677280048026624826249302,
                    .7199319220394659358894349533527348
                    ),
                _s211(
                    .2044800806367957142413355748727453,
                    .5805771901288092241753981713906204
                    ),
                ])
            self.degree = 8
        elif index == 2:
            self.weights = numpy.concatenate([
                .0040651136652707670436208836835636 * numpy.ones(4),
                .0022145385334455781437599569500071 * numpy.ones(4),
                .0058134382678884505495373338821455 * numpy.ones(4),
                .0196255433858357215975623333961715 * numpy.ones(4),
                .0003875737905908214364538721248394 * numpy.ones(4),
                .0116429719721770369855213401005552 * numpy.ones(12),
                .0052890429882817131317736883052856 * numpy.ones(12),
                .0018310854163600559376697823488069 * numpy.ones(12),
                .0082496473772146452067449669173660 * numpy.ones(12),
                .0030099245347082451376888748208987 * numpy.ones(24),
                .0008047165617367534636261808760312 * numpy.ones(24),
                .0029850412588493071187655692883922 * numpy.ones(24),
                .0056896002418760766963361477811973 * numpy.ones(24),
                .0041590865878545715670013980182613 * numpy.ones(24),
                .0007282389204572724356136429745654 * numpy.ones(24),
                .0054326500769958248216242340651926 * numpy.ones(24),
                ])
            bary = numpy.concatenate([
                _s31(.3272533625238485639093096692685289),
                _s31(.0447613044666850808837942096478842),
                _s31(.0861403311024363536537208740298857),
                _s31(.2087626425004322968265357083976176),
                _s31(.0141049738029209600635879152102928),
                _s211(
                    .1021653241807768123476692526982584,
                    .5739463675943338202814002893460107
                    ),
                _s211(
                    .4075700516600107157213295651301783,
                    .0922278701390201300000000000000000
                    ),
                _s211(
                    .0156640007402803585557586709578084,
                    .7012810959589440327139967673208426
                    ),
                _s211(
                    .2254963562525029053780724154201103,
                    .4769063974420887115860583354107011
                    ),
                _s1111(
                    .3905984281281458000000000000000000,
                    .2013590544123922168123077327235092,
                    .0161122880710300298578026931548371
                    ),
                _s1111(
                    .1061350679989021455556139029848079,
                    .0327358186817269284944004077912660,
                    .0035979076537271666907971523385925
                    ),
                _s1111(
                    .5636383731697743896896816630648502,
                    .2302920722300657454502526874135652,
                    .1907199341743551862712487790637898
                    ),
                _s1111(
                    .3676255095325860844092206775991167,
                    .2078851380230044950717102125250735,
                    .3312104885193449000000000000000000
                    ),
                _s1111(
                    .7192323689817295295023401840796991,
                    .1763279118019329762157993033636973,
                    .0207602362571310090754973440611644
                    ),
                _s1111(
                    .5278249952152987298409240075817276,
                    .4372890892203418165526238760841918,
                    .0092201651856641949463177554949220
                    ),
                _s1111(
                    .5483674544948190728994910505607746,
                    .3447815506171641228703671870920331,
                    .0867217283322215394629438740085828
                    ),
                ])
            self.degree = 14
        else:
            raise ValueError('Illegal Zhang index')

        self.points = bary[:, [1, 2, 3]]
        return


class ShunnHam(object):
    '''
    Lee Shunn, Frank Ham,
    Symmetric quadrature rules for tetrahedra based on a cubic
    close-packed lattice arrangement,
    Journal of Computational and Applied Mathematics,
    2012,
    <http://dx.doi.org/10.1016/j.cam.2012.03.032>.

    Abstract:
    A family of quadrature rules for integration over tetrahedral volumes is
    developed. The underlying structure of the rules is based on the cubic
    close-packed (CCP) lattice arrangement using 1, 4, 10, 20, 35, and 56
    quadrature points. The rules are characterized by rapid convergence,
    positive weights, and symmetry. Each rule is an optimal approximation in
    the sense that lower-order terms have zero contribution to the truncation
    error and the leading-order error term is minimized. Quadrature formulas up
    to order 9 are presented with relevant numerical examples.
    '''
    def __init__(self, index):
        if index == 1:
            self.weights = numpy.array([
                1.0
                ])
            bary = _s4()
            self.degree = 1
        elif index == 2:
            self.weights = 0.25 * numpy.ones(4)
            bary = _s31(0.1381966011250110)
            self.degree = 2
        elif index == 3:
            self.weights = numpy.concatenate([
                0.0476331348432089 * numpy.ones(4),
                0.1349112434378610 * numpy.ones(6),
                ])
            bary = numpy.concatenate([
                _s31(0.0738349017262234),
                _s22(0.0937556561159491),
                ])
            self.degree = 3
        elif index == 4:
            self.weights = numpy.concatenate([
                0.0070670747944695 * numpy.ones(4),
                0.0469986689718877 * numpy.ones(12),
                0.1019369182898680 * numpy.ones(4),
                ])
            bary = numpy.concatenate([
                _s31(0.0323525947272439),
                _s211(0.0603604415251421, 0.2626825838877790),
                _s31(0.3097693042728620),
                ])
            self.degree = 5
        elif index == 5:
            self.weights = numpy.concatenate([
                0.0021900463965388 * numpy.ones(4),
                0.0143395670177665 * numpy.ones(12),
                0.0250305395686746 * numpy.ones(6),
                0.0479839333057554 * numpy.ones(12),
                0.0931745731195340 * numpy.ones(1)
                ])
            bary = numpy.concatenate([
                _s31(0.0267367755543735),
                _s211(0.0391022406356488, 0.7477598884818090),
                _s22(0.0452454000155172),
                _s211(0.2232010379623150, 0.0504792790607720),
                numpy.array([[0.25, 0.25, 0.25, 0.25]]),
                ])
            self.degree = 6
        elif index == 6:
            self.weights = numpy.concatenate([
                0.0010373112336140 * numpy.ones(4),
                0.0096016645399480 * numpy.ones(12),
                0.0164493976798232 * numpy.ones(12),
                0.0153747766513310 * numpy.ones(12),
                0.0293520118375230 * numpy.ones(12),
                0.0366291366405108 * numpy.ones(4),
                ])
            bary = numpy.concatenate([
                _s31(0.0149520651530592),
                _s211(0.0340960211962615, 0.1518319491659370),
                _s211(0.0462051504150017, 0.5526556431060170),
                _s211(0.2281904610687610, 0.0055147549744775),
                _s211(0.3523052600879940, 0.0992057202494530),
                _s31(0.1344783347929940)
                ])
            self.degree = 7
        else:
            raise ValueError('Illegal Shunn-Ham index')

        self.points = bary[:, 1:]
        return