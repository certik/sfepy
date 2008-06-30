import os.path as op
import re
import types
import sys

from base import Struct, IndexedStruct, dictToStruct, pause, output, copy
from reader import Reader

_required = ['fileName_mesh', 'field_[0-9]+|fields',
             'ebc_[0-9]+|ebcs', 'fe', 'equations',
             'region_[0-9]+|regions', 'variable_[0-9]+|variables',
             'material_[0-9]+|materials', 'integral_[0-9]+|integrals',
             'solver_[0-9]+|solvers']
_other = ['functions', 'modules', 'epbc_[0-9]+|epbcs',
          'lcbc_[0-9]+|lcbcs', 'nbc_[0-9]+|nbcs', 'options']

##
# c: 19.02.2008, r: 19.02.2008
def getStandardKeywords():
    return copy( _required ), copy( _other )

##
# c: 10.04.2008, r: 10.04.2008
def tupleToConf( name, vals, order ):
    conf = Struct( name = name )
    for ii, key in enumerate( order ):
        setattr( conf, key, vals[ii] )
    return conf

##
# Short syntax: key is suffixed with '_' to prevent collisions with long syntax
# keys -> both cases can be used in a single input.

##
# c: 10.04.2008, r: 06.05.2008
def transform_variables( adict ):
    d2 = {}
    for ii, (key, conf) in enumerate( adict.iteritems() ):
        if isinstance( conf, tuple ):
            c2 = tupleToConf( key, conf, ['kind', 'field'] )
            if len( conf ) == 3:
                kind = c2.kind.split()[0]
                if kind == 'unknown':
                    c2.order = conf[2]
                elif kind == 'test':
                    c2.dual = conf[2]
                elif kind == 'parameter':
                    c2.like = conf[2]
            d2['variable__%d' % ii] = c2
        else:
            c2 = transform_toStruct_1( conf )
            d2[key] = c2
    return d2

##
# c: 10.04.2008, r: 06.05.2008
def transform_ebcs( adict ):
    d2 = {}
    for ii, (key, conf) in enumerate( adict.iteritems() ):
        if isinstance( conf, tuple ):
            c2 = tupleToConf( key, conf, ['region', 'dofs'] )
            d2['ebc__%d' % ii] = c2
        else:
            c2 = transform_toStruct_1( conf )
            d2[key] = c2
    return d2

##
# c: 02.05.2008, r: 06.05.2008
def transform_regions( adict ):
    d2 = {}
    for ii, (key, conf) in enumerate( adict.iteritems() ):
        if isinstance( conf, tuple ):
            c2 = tupleToConf( key, conf, ['select', 'flags'] )
            for flag, val in c2.flags.iteritems():
                setattr( c2, flag, val )
            delattr( c2, 'flags' )
            d2['region__%d' % ii] = c2
        else:
            c2 = transform_toStruct_1( conf )
            d2[key] = c2
    return d2

##
# c: 20.06.2007, r: 18.02.2008
def transform_toStruct_1( adict ):
    return dictToStruct( adict, flag = (1,) )
def transform_toIStruct_1( adict ):
    return dictToStruct( adict, flag = (1,), constructor = IndexedStruct )
def transform_toStruct_01( adict ):
    return dictToStruct( adict, flag = (0,1) )
def transform_toStruct_10( adict ):
    return dictToStruct( adict, flag = (1,0) )

transforms = {
    'options'   : transform_toIStruct_1,
    'solvers'   : transform_toStruct_01,
    'integrals' : transform_toStruct_01,
    'opt'       : transform_toStruct_1,
    'fe'        : transform_toStruct_1,
    'regions'   : transform_regions,
    'shapeOpt'  : transform_toStruct_10,
    'fields'    : transform_toStruct_01,
    'variables' : transform_variables,
    'ebcs'      : transform_ebcs,
    'epbcs'     : transform_toStruct_01,
    'nbcs'      : transform_toStruct_01,
    'lcbcs'     : transform_toStruct_01,
}

##
# 27.10.2005, c
class ProblemConf( Struct ):
    ##
    # 25.07.2006, c
    # 19.09.2006
    # 16.10.2006
    # 31.05.2007
    # 05.06.2007
    def fromFile( fileName, required = None, other = None ):
        sys.path.append( op.dirname( fileName ) )
        read = Reader( '.' )
        obj = read( ProblemConf, op.splitext( fileName )[0] )
        otherMissing = obj.validate( required = required, other = other )
        for name in otherMissing:
            setattr( obj, name, None )
        obj._fileName = fileName
        obj.transformInput()
        return obj
    fromFile = staticmethod( fromFile )

    ##
    # 20.06.2007, c
    def fromModule( module, required = None, other = None ):
        obj = ProblemConf()
        obj.__dict__.update( module.__dict__ )
        return obj
    fromModule = staticmethod( fromModule )

    ##
    # 27.10.2005, c
    # 19.09.2006
    # 05.06.2007
    def _validateHelper( self, items, butNots ):
        keys = self.__dict__.keys()
        leftOver = keys[:]
        if butNots is not None:
            for item in butNots:
                match = re.compile( '^' + item + '$' ).match
                for key in keys:
                    if match( key ):
                        leftOver.remove( key )

        missing = []
        if items is not None:
            for item in items:
                found = False
                match = re.compile( '^' + item + '$' ).match
                for key in keys:
                    if match( key ):
                        found = True
                        leftOver.remove( key )
                if not found:
                    missing.append( item )
        return leftOver, missing

    ##
    # c: 27.10.2005, r: 20.02.2008
    def validate( self, required = None, other = None ):
        requiredLeftOver, requiredMissing \
                          = self._validateHelper( required, other )
        otherLeftOver, otherMissing \
                       = self._validateHelper( other, required )

        assert requiredLeftOver == otherLeftOver

        err = False
        if requiredMissing:
            err = True
            output( 'error: required missing:', requiredMissing )

        if otherMissing:
            output( 'warning: other missing:', otherMissing )

        if otherLeftOver:
            output( 'warning: left over:', otherLeftOver )

        if err:
            raise ValueError

        return otherMissing

    ##
    # c: 31.10.2005, r: 18.02.2008
    def transformInput( self ):
        """Trivial input transformations."""

        ##
        # Unordered inputs.
        trList = ['([a-zA-Z0-9]+)_[0-9]+']
        # Keywords not in 'required', but needed even empty (e.g. for runTests).
        for key in transforms.keys():
            if not self.__dict__.has_key( key ):
                self.__dict__[key] = {}

        keys = self.__dict__.keys()
        for item in trList:
            match = re.compile( item ).match
            for key in keys:
                obj = match( key )
                if obj:
                    new = obj.group( 1 ) + 's'
                    result = {key : self.__dict__[key]}
                    try:
                        self.__dict__[new].update( result )
                    except:
                        self.__dict__[new] = result
                        
                    del self.__dict__[key]

        keys = self.__dict__.keys()
        for key, transform in transforms.iteritems():
            if not key in keys: continue
            self.__dict__[key] = transform( self.__dict__[key] )

        # Make module from the input file.
        name = op.splitext( op.basename( self._fileName ) )[0]
        self.funmod = __import__( name )