import sympy as sp
from sympy import sin, cos, Plot, Basic, Symbol, sympify, zeronm, lambdify,\
     symbols
from sympy.abc import x, y, z, t

from numpy import arange, zeros
import numpy as nm

dim = 3
def set_dim( dim ):
    globals()['dim'] = dim
    
def default_space_variables( variables ):
    if variables is None:
        variables = [x, y, z][:dim]
    return variables

def grad( f, variables = None ):
    variables = default_space_variables( variables )
    nVar = len( variables )
#    import pdb; pdb.set_trace()
    f = sp.sympify( f )

    out = sp.zeronm( nVar, 1)
    for iv, var in enumerate( variables ):
       out[iv,0] = f.diff( var )
    return out

##
# c: 09.06.2008, r: 09.06.2008
def gradV( f, variables = None ):
    variables = default_space_variables( variables )
    nVar = len( variables )

    f = sympify( f )
    out = zeros( (nVar,) + f.shape )
    for iv, var in enumerate( variables ):
       out[iv,...] = f.diff( var )
    return out

def div( field, variables = None ):
    variables = default_space_variables( variables )
    nVar = len( variables )

    field = list( field )
    assert len( field ) == nVar

    out = 0
    for f_i, x_i in zip( field, variables ):
        out += sp.sympify( f_i ).diff( x_i )
#    import pdb; pdb.set_trace()
    return out

def laplace( f, variables = None ):
    return div( grad( f, variables ), variables)

def boundary(f, variables):
    lap = laplace(f, variables)
    l = lambdify(lap, variables)
    a = 5.
    for x in arange(-a, a, 0.1):
        y = -a
        print x, y, l(x, y)

if __name__ == '__main__':
    f = sin(x)*cos(y)
    boundary(f, [x, y])
    #Plot(f, [x, -10, 10], [y, -10, 10])

    set_dim( 2 )

    f = 'sin( 3.0 * x ) * cos( 4.0 * y )'
    A = sp.Matrix( [[1, 0.1], [0.1, 2]] )

    gf = grad( f )
    agf = A * gf