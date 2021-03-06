# c: 05.05.2008, r: 05.05.2008
import sys
sys.path.append( '.' )

from sfepy.fem.periodic import *

# c: 05.05.2008, r: 05.05.2008
def define_regions( filename ):
    """Define various subdomain for a given mesh file. This function is called
    below."""
    regions = {}
    is3d = False
    
    regions['Y'] = ('all', {})

    eog = 'elements of group %d'
    if filename.find( 'osteonT1' ) >= 0:
        mat_ids = [11, 39, 6, 8, 27, 28, 9, 2, 4, 14, 12, 17, 45, 28, 15]
        regions['Ym'] = (' +e '.join( (eog % im) for im in  mat_ids ), {})
        wx = 0.865
        wy = 0.499

    regions['Yc'] = ('r.Y -e r.Ym', {})

    # Sides.
    regions['Left'] = ('nodes in (x < -%.3f)' % wx, {})
    regions['Right'] = ('nodes in (x > %.3f)' % wx, {})
    regions['Bottom'] = ('nodes in (y < -%.3f)' % wy, {})
    regions['Top'] = ('nodes in (y > %.3f)' % wy, {})
    regions['Corners'] = ("""nodes in
                            ((x < -%.3f) & (y < -%.3f))
                          | ((x >  %.3f) & (y < -%.3f))
                          | ((x >  %.3f) & (y >  %.3f))
                          | ((x < -%.3f) & (y >  %.3f))
                          """ % ((wx, wy) * 4), {})
    return is3d, regions, mat_ids

##
# c: 05.05.2008, r: 05.05.2008
def get_pars( ts, coor, region, ig, mat_ids = [] ):
    """Define material parameters:
         $D_ijkl$ (elasticity),
       in a given region."""
    dim = coor.shape[1]
    sym = (dim + 1) * dim / 2

    m2i = region.domain.mat_ids_to_i_gs
    matrix_igs = [m2i[im] for im in mat_ids]

    out = {}

    # in 1e+10 [Pa]
    lam = 1.7
    mu = 0.3
    o = nm.array( [1.] * dim + [0.] * (sym - dim), dtype = nm.float64 )
    oot = nm.outer( o, o )
    out['D'] = lam * oot + mu * nm.diag( o + 1.0 )

    if ig not in matrix_igs: # channels
        out['D'] *= 1e-1

    return out
    
##
# Mesh file.
filename_mesh = 'examples/osteonT1_11.mesh'

##
# Define regions (subdomains, boundaries) - $Y$, $Y_i$, ...
# depending on a mesh used.
is3d, regions, mat_ids = define_regions( filename_mesh )

if is3d:
    dim, geom = 3, '3_4'
else:
    dim, geom = 2, '2_3'

##
# Define fields: 'displacement' in $Y$,
# 'pressure_m' in $Y_m$.
field_1 = {
    'name' : 'displacement',
    'dim' : (dim,1),
    'domain' : 'Y',
    'bases' : {'Y' : '%s_P1' % geom}
}

field_2 = {
    'name' : 'pressure_m',
    'dim' : (1,1),
    'domain' : 'Ym',
    'bases' : {'Ym' : '%s_P1' % geom}
}

##
# Define corrector variables: unknown displaements: uc, test: vc
# displacement-like variables: Pi, Pi1, Pi2
variables = {
    'uc'       : ('unknown field',   'displacement', 0),
    'vc'       : ('test field',      'displacement', 'uc'),
    'Pi'       : ('parameter field', 'displacement', 'uc'),
    'Pi1'      : ('parameter field', 'displacement', 'uc'),
    'Pi2'      : ('parameter field', 'displacement', 'uc'),
}

##
# Periodic boundary conditions.
if dim == 3:
    epbc_10 = {
        'name' : 'periodic_x',
        'region' : ['Left', 'Right'],
        'dofs' : {'uc.all' : 'uc.all'},
        'match' : 'match_x_plane',
    }
    epbc_11 = {
        'name' : 'periodic_y',
        'region' : ['Near', 'Far'],
        'dofs' : {'uc.all' : 'uc.all'},
        'match' : 'match_y_plane',
    }
    epbc_12 = {
        'name' : 'periodic_z',
        'region' : ['Top', 'Bottom'],
        'dofs' : {'uc.all' : 'uc.all'},
        'match' : 'match_z_plane',
    }
else:
    epbc_10 = {
        'name' : 'periodic_x',
        'region' : ['Left', 'Right'],
        'dofs' : {'uc.all' : 'uc.all'},
        'match' : 'match_y_line',
    }
    epbc_11 = {
        'name' : 'periodic_y',
        'region' : ['Top', 'Bottom'],
        'dofs' : {'uc.all' : 'uc.all'},
        'match' : 'match_x_line',
    }
    
##
# Dirichlet boundary conditions.
ebcs = {
    'fixed_u' : ('Corners', {'uc.all' : 0.0}),
}

##
# Material defining constitutive parameters of the microproblem.
material_1 = {
    'name' : 'm',
    'mode' : 'function',
    'region' : 'Y',
    'function' : 'get_pars',
    'extra_args' : {'mat_ids' : mat_ids},
}

##
# Numerical quadratures for volume (i3 - order 3) integral terms.
integral_1 = {
    'name' : 'i3',
    'kind' : 'v',
    'quadrature' : 'gauss_o3_d%d' % dim,
}

##
# Homogenized coefficients to compute.
coefs = {
    'E' : {'requires' : ['pis', 'corrs_rs'],
           'variables' : ['Pi1', 'Pi2'],
           'region' : 'Y',
           'expression' : 'dw_lin_elastic.i3.Y( m.D, Pi1, Pi2 )'},
}

##
# Data required to compute the homogenized coefficients.
all_periodic = ['periodic_%s' % ii for ii in ['x', 'y', 'z'][:dim] ]
requirements = {
    'pis' : {
        'variables' : ['uc'],
    },
    ##
    # Steady state correctors $\bar{\omega}^{rs}$.
    'corrs_rs' : {
         'variables' : ['uc', 'vc', 'Pi'],
         'ebcs' : ['fixed_u'],
         'epbcs' : all_periodic,
         'equations' : {'eq' : """dw_lin_elastic.i3.Y( m.D, vc, uc )
                                = - dw_lin_elastic.i3.Y( m.D, vc, Pi )"""},
    },
}

##
# FE assembling options.
fe = {
    'chunk_size' : 100000,
    'cache_override' : True,
}

##
# Solvers.
solver_0 = {
    'name' : 'ls',
    'kind' : 'ls.umfpack', # Direct solver.
}

solver_1 = {
    'name' : 'newton',
    'kind' : 'nls.newton',

    'i_max'      : 2,
    'eps_a'      : 1e-8,
    'eps_r'      : 1e-2,
    'macheps'   : 1e-16,
    'lin_red'    : 1e-2, # Linear system error < (eps_a * lin_red).
    'ls_red'     : 0.1,
    'ls_red_warp' : 0.001,
    'ls_on'      : 0.99999,
    'ls_min'     : 1e-5,
    'check'     : 0,
    'delta'     : 1e-6,
    'is_plot'    : False,
    'problem'   : 'nonlinear', # 'nonlinear' or 'linear' (ignore i_max)
}

############################################
# Mini-application below, computing the homogenized elastic coefficients.

def make_save_hook( base_name, post_process_hook = None, file_per_var = None ):
    """Returns function used to save the computed correctors."""
    def save_correctors( state, problem, ir, ic ):
        get_state = problem.variables.get_state_part_view

        problem.save_state( (base_name % (ir, ic)) + '.vtk', state,
                            post_process_hook = post_process_hook,
                            file_per_var = file_per_var )
    return save_correctors

##
# c: 05.05.2008, r: 28.11.2008
def main():
    from sfepy.base.base import spause
    from sfepy.base.conf import ProblemConf, get_standard_keywords
    from sfepy.fem import eval_term_op, ProblemDefinition
    from sfepy.homogenization.utils import create_pis
    from sfepy.homogenization.coefs import CorrectorsRS, ElasticCoef

    nm.set_printoptions( precision = 3 )

    spause( r""">>>
First, this file will be read in place of an input
(problem description) file.
Press 'q' to quit the example, press any other key to continue...""" )
    required, other = get_standard_keywords()
    required.remove( 'equations' )
    # Use this file as the input file.
    conf = ProblemConf.from_file( __file__, required, other )
    print conf.to_dict().keys()
    spause( r""">>>
...the read input as a dict (keys only for brevity).
['q'/other key to quit/continue...]""" )

    spause( r""">>>
Now the input will be used to create a ProblemDefinition instance.
['q'/other key to quit/continue...]""" )
    problem = ProblemDefinition.from_conf( conf,
                                          init_variables = False,
                                          init_equations = False )
    print problem
    spause( r""">>>
...the ProblemDefinition instance.
['q'/other key to quit/continue...]""" )


    spause( r""">>>
The homogenized elastic coefficient $E_{ijkl}$ is expressed
using $\Pi$ operators, computed now. In fact, those operators are permuted
coordinates of the mesh nodes.
['q'/other key to quit/continue...]""" )
    req = conf.requirements['pis']
    pis = create_pis( problem, req['variables'][0] )
    print pis
    spause( r""">>>
...the $\Pi$ operators.
['q'/other key to quit/continue...]""" )

    spause( r""">>>
Next, $E_{ijkl}$ needs so called steady state correctors $\bar{\omega}^{rs}$,
computed now. The results will be saved in: %s_*.vtk
['q'/other key to quit/continue...]""" %  problem.ofn_trunk )

    save_hook = make_save_hook( problem.ofn_trunk + '_rs_%d%d' )

    req = conf.requirements['corrs_rs']
    solve_corrs = CorrectorsRS( 'steady rs correctors', problem, req )
    corrs_rs = solve_corrs( data = pis, save_hook = save_hook )
    print corrs_rs
    spause( r""">>>
...the $\bar{\omega}^{rs}$ correctors.
['q'/other key to quit/continue...]""" )

    spause( r""">>>
Then the volume of the domain is needed.
['q'/other key to quit/continue...]""" )
    volume = eval_term_op( None, 'd_volume.i3.Y( uc )', problem )
    print volume

    spause( r""">>>
...the volume.
['q'/other key to quit/continue...]""" )

    spause( r""">>>
Finally, $E_{ijkl}$ can be computed.
['q'/other key to quit/continue...]""" )
    get_coef = ElasticCoef( 'homogenized elastic tensor',
                            problem, conf.coefs['E'] )
    c_e = get_coef( volume, data = {'pis': pis, 'corrs' : corrs_rs} )
    print r""">>>
The homogenized elastic coefficient $E_{ijkl}$, symmetric storage
with rows, columns in 11, 22, 12 ordering:"""
    print c_e
    
if __name__ == '__main__':
    main()
