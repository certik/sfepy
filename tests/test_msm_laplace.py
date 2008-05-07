# c: 07.05.2007, r: 07.05.2008
fileName_mesh = 'database/phono/mesh_circ21.mesh'

field_1 = {
    'name' : 'a_harmonic_field',
    'dim' : (1,1),
    'domain' : 'Omega',
    'bases' : {'Omega' : '2_3_P1'}
}

variables = {
    't': ('unknown field', 'a_harmonic_field', 0),
    's': ('test field',    'a_harmonic_field', 't'),
}

regions = {
    'Omega' : ('all', {}),
    'Left' : ('nodes in (x < 0.001) & (y < 0.001)', {}),
    'Right' : ('nodes in (x > 0.999)', {}),
    'Gamma' : ('nodes of surface', {}),
}

ebcs = {
    't_left' : ('Gamma', {'t.0' : 'ebc'}),
#    't_right' : ('Right', {'t.0' : 'ebc'}),
}

integral_1 = {
    'name' : 'i1',
    'kind' : 'v',
    'quadrature' : 'gauss_o2_d2',
}

material_1 = {
    'name' : 'coef',
    'mode' : 'here',
    'region' : 'Omega',
    'val' : 1.0,
}

material_2 = {
    'name' : 'rhs',
    'mode' : 'function',
    'region' : 'Omega',
    'function' : 'rhs',
    'extraArgs' : {'expression' : None},
}

equations = {
    'Temperature' :
    """dw_laplace.i1.Omega( coef.val, s, t )
       = dw_volume_lvf.i1.Omega( rhs.val, s )"""
}

solutions = {
    'sincos' : ('t', 'nm.sin( 3.0 * x ) * nm.cos( 4.0 * y )',
                '25.0 * nm.sin( 3.0 * x ) * nm.cos( 4.0 * y )'),
    'poly' : ('t', '(x**2) + (y**2)', '[-4.0]'),
    'polysin' : ('t', '((x - 0.5)**3) * nm.sin( 5.0 * y )',
                 '- 6.0 * (x - 0.5) * nm.sin( 5.0 * y ) + 25.0 * ((x - 0.5)**3) * nm.sin( 5.0 * y )'),
}

solver_0 = {
    'name' : 'ls',
    'kind' : 'ls.umfpack',
}

solver_1 = {
    'name' : 'newton',
    'kind' : 'nls.newton',

    'iMax'      : 1,
    'epsA'      : 1e-10,
    'epsR'      : 1.0,
    'macheps'   : 1e-16,
    'linRed'    : 1e-2, # Linear system error < (epsA * linRed).
    'lsRed'     : 0.1,
    'lsRedWarp' : 0.001,
    'lsOn'      : 1.1,
    'lsMin'     : 1e-5,
    'check'     : 0,
    'delta'     : 1e-6,
    'isPlot'    : False,
    'linSolver' : 'umfpack',
    'problem'   : 'nonlinear', # 'nonlinear' or 'linear' (ignore iMax)
}

fe = {
    'chunkSize' : 100000
}

import numpy as nm
from sfe.base.testing import TestCommon
from sfe.base.base import debug, pause
outputName = 'test_msm_laplace_%s.vtk'

##
# c: 07.05.2007, r: 07.05.2008
solution = ['']
def ebc( bc, ts, coor, solution = solution ):
    expression = solution[0]
    val = TestCommon.evalCoorExpression( expression, coor )
    return val

##
# c: 07.05.2007, r: 07.05.2008
def rhs( ts, coor, region, ig, expression = None ):
    if expression is None:
        expression = '0.0 * x'

    val = TestCommon.evalCoorExpression( expression, coor )
    return {'val' : val}

##
# c: 07.05.2007
class Test( TestCommon ):

    ##
    # c: 07.05.2007, r: 07.05.2008
    def fromConf( conf, options ):
        from sfe.fem.problemDef import ProblemDefinition

        problem = ProblemDefinition.fromConf( conf )
        test = Test( problem = problem,
                     conf = conf, options = options )
        return test
    fromConf = staticmethod( fromConf )

    ##
    # c: 07.05.2007, r: 07.05.2008
    def test_msm_laplace( self ):
        import pylab
        import os.path as op
        
        sols = self.conf.solutions
        problem  = self.problem

        ok = True
        for solName, sol in sols.iteritems():
            self.report( 'testing', solName )
            varName, solExpr, rhsExpr = sol

            self.report( 'sol:', solExpr )
            self.report( 'rhs:', rhsExpr )
            matArgs = {'rhs' : {'expression' : rhsExpr}} 
            globals()['solution'][0] = solExpr
            problem.timeUpdate( extraMatArgs = matArgs )
            problem.equations.resetTermCaches()
            vec = problem.solve()
            coor = problem.variables[varName].field.getCoor()
            anaSol = self.evalCoorExpression( solExpr, coor )
            numSol = problem.variables.getStatePartView( vec, varName )

##             from sfe.fem.evaluate import evalTermOP
##             aa = evalTermOP( anaSol, "dw_laplace.i1.Omega( coef.val, s, t )",
##                              problem, dwMode = 'vector' )
##             print aa
##             aa = evalTermOP( numSol, "dw_laplace.i1.Omega( coef.val, s, t )",
##                              problem, dwMode = 'vector' )
##             print aa
##             aa = evalTermOP( numSol, "dw_volume_lvf.i1.Omega( rhs.val, s )",
##                              problem, dwMode = 'vector' )
##             print aa
##             pause()

##             pylab.plot( anaSol )
##             pylab.plot( numSol )
##             pylab.show()
            anaNorm = nm.linalg.norm( anaSol, nm.inf )
            ret = self.compareVectors( anaSol, numSol,
                                       allowedError = anaNorm * 1e-2,
                                       label1 = 'analytical %s' % varName,
                                       label2 = 'numerical %s' % varName,
                                       norm = nm.inf )
            if not ret:
                self.report( 'variable %s: failed' % varName )

            fname = op.join( self.options.outDir, self.conf.outputName )
            out = {}
            aux = problem.stateToOutput( anaSol )
            out['ana_t'] = aux['t']
            aux = problem.stateToOutput( numSol )
            out['num_t'] = aux['t']

            problem.domain.mesh.write( fname % solName, io = 'auto', out = out )

            ok = ok and ret

        return ok