#!/usr/bin/env python
import os
import os.path as op
from optparse import OptionParser
import pyparsing as pp

from sfe.base.base import *
from sfe.terms import termTable, cacheTable

##
# 09.11.2007, c
# 13.11.2007
def setSection( sec ):
    def action( str, loc, toks ):
        if toks:
            sec[0] = toks[0][1:-1]
        return toks
    return action

##
# 09.11.2007, c
def toList( slist, sec ):
    def action( str, loc, toks ):
        if toks:
##             print toks
##             pause()
            slist.append( (sec[0], toks[0]) )
        return toks
    return action
    
##
# 09.11.2007, c
# 13.11.2007
def createBNF( slist, currentSection ):
    
    colon = pp.Literal( ':' )

    section = pp.Combine( colon
                          + pp.Word( pp.alphas, pp.alphanums + '_ ' )
                          + colon )
    section.setParseAction( setSection( currentSection ) )
    section.setName( 'section' )
#    section.setDebug()

    text = pp.SkipTo( section | pp.StringEnd() )
    text.setParseAction( toList( slist, currentSection ) )
    text.setName( 'text' )
#    text.setDebug()

##     doc = pp.StringStart()\
##           + pp.ZeroOrMore( section + text )\
##           + pp.StringEnd()

    doc = pp.StringStart()\
           + pp.Optional( text ) + pp.ZeroOrMore( section + text )\
           + pp.StringEnd()

    return doc

outputDir = './tmp'

defines = r"""
\def\dt{{\Delta t}}
\def\pdiff#1#2{\frac{\partial {#1}}{\partial {#2}}}
\def\difd#1{\ {\rm d}#1}
\newcommand{\dvg}{\mathop{\rm div}}
\newcommand{\ul}[1]{\underline{#1}}
\newcommand{\uld}[1]{\dot{\underline{#1}}}
\newcommand{\ull}[1]{\underline{\underline{#1}}}
\def\Vcal{\mathcal{V}}
\def\Tcal{\mathcal{T}}
\def\figDir{../doc/tex/figures}
\newcommand{\sfe}{SFE}
"""

header = r"""
\documentclass[10pt,a4paper]{article}

\usepackage{bm}
\usepackage{a4wide}

%s
"""  % defines

begining = r"""
<article>
<title>SfePy Documentation</title>

"""

ending = r"""
</article>
"""

itemSection = r"""
<em>%s</em>:
"""

termSyntax = r"""
%s.%s( &lt;%s> )
"""            

cacheSyntax = r"""{
\small
\begin{verbatim}
cache = term.getCache( '%s', &lt;index> )
data = cache( &lt;data name>, &lt;ig>, &lt;ih>, %s )
\end{verbatim}
}"""            

termDefinition = r"""
<e> %s </e>
"""

##
# 29.10.2007, c
# 15.11.2007
def itemsPerSections( table, secNamePrefix, omitList ):
    if omitList is not None:
        omitList = omitList.split()

    ips = {}
    for name, cls in table.iteritems():
        module = cls.__module__.split( '.' )[-1]
        if module in omitList: continue
        secName = '%s in %s' % (secNamePrefix, module)
        ips.setdefault( secName, [] ).append( name )
    return ips

##
# c: 14.11.2007, r: 24.10.2008
def typesetTermSyntax( fd, cls, name ):
    fd.write( itemSection % 'Syntax' )
    argTypes = '>, &lt;'.join( cls.argTypes )
    fd.write( termSyntax % (name, '&lt;i>.&lt;r>', argTypes) )

##
# 14.11.2007, c
def typesetCacheSyntax( fd, cls, name ):
    argTypes = ', '.join( cls.argTypes )
    fd.write( cacheSyntax % (name, argTypes) )

##
# 15.11.2007, c
def typesetArguments( fd, argsText ):
    fd.write( r'\begin{center}' )
    fd.write( '\n' )
    aux = argsText.split( ',' )
    fd.write( r'\begin{tabular}{rcl}' )
    fd.write( '\n' )
    for argDesc in aux:
        print argDesc
        args = argDesc.split( r':' )
        fd.write( r'%s &amp; \dots &amp; %s \\' % (args[0], args[1]) )
        fd.write( '\n' )

    fd.write( r'\end{tabular}' )
    fd.write( '\n' )
    fd.write( r'\end{center}' )
    fd.write( '\n' )

##
# 14.11.2007, c
def typeset( fd, itemsPerSection, itemTable, typesetSyntax ):
    secList = []
    currentSection = [None]
    bnf = createBNF( secList, currentSection )

    for secName, itemNames in itemsPerSection.iteritems():
        fd.write( r'<section><title>%s</title>' % secName )
        fd.write( '\n\n' )

        itemNames.sort()
        for itemName in itemNames:
            itemClass = itemTable[itemName]
            name = itemClass.name#.replace( '_', '\_' )
            fd.write( r'<section><title>%s</title>' %  name )
            fd.write( '\n' )
            fd.write( r'\textbf{Class}: %s' % itemClass.__name__ )
            fd.write( '\n\n' )

            doc = itemClass.__doc__
            if doc is not None:
                print doc
                secList[:] = []
                currentSection[0] = None
                out = bnf.parseString( doc )
##                 print secList
##                 pause()

                for secName, secText in secList:
#                    print secName
#                    print secText
                    if secName is None and not secText: continue
                    if secName is not None:
                        fd.write( itemSection % secName.capitalize() )
                        if secName == 'definition':
                            secText = secText.replace("$", "")
                            fd.write( termDefinition % secText )
                            fd.write( '\n\n' )
                        elif secName == 'arguments':
                            typesetArguments( fd, secText )
                        else:
                            fd.write( secText )
                            fd.write( '\n\n' )

            typesetSyntax( fd, itemClass, itemName )
            fd.write( r'</section>' )
        fd.write( r'</section>' )

usage = """%prog [options]"""
help = {
    'omit' :
    'omit listed sections',
}

# ./genDocs.py --omit="termsAdjointNavierStokes termsHDPM  cachesHDPM  cachesBasic"

##
# c: 29.10.2007, r: 24.01.2008
def main():
    parser = OptionParser( usage = usage, version = "%prog" )
    parser.add_option( "", "--omit", metavar = 'list of sections',
                       action = "store", dest = "omitList",
                       default = "", help = help['omit'] )
    (options, args) = parser.parse_args()

    tps = itemsPerSections( termTable, 'Terms', options.omitList )
    cps = itemsPerSections( cacheTable, 'Term caches', options.omitList )

    latexFileName = 'terms.xml'
    latexFileNameComplete = op.join( outputDir, latexFileName )
    print latexFileNameComplete

    fd = open( latexFileNameComplete, 'w' )
#    fd.write( header )
    fd.write( begining )

    typeset( fd, tps, termTable, typesetTermSyntax )
    typeset( fd, cps, cacheTable, typesetCacheSyntax )
            
    fd.write( ending )
    fd.close()

if __name__ == '__main__':
    main()