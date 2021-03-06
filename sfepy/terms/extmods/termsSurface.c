#include "termsSurface.h"
#include "terms.h"
#include "geommech.h"

#undef __FUNC__
#define __FUNC__ "dw_surface_ltr"
/*!
  @par Revision history:
  - 06.09.2006, c
  - 11.10.2006
*/
int32 dw_surface_ltr( FMField *out, FMField *bf, FMField *gbf,
		      FMField *traction, SurfaceGeometry *sg,
		      int32 *conn, int32 nEl, int32 nEP,
		      int32 *elList, int32 elList_nRow )
{
  int32 ii, iel, dim, sym, nQP, nFP, ret = RET_OK;
  FMField *trac = 0, *tracQP = 0, *outQP = 0, *pn = 0, *stn = 0;

  nFP = bf->nCol;
  nQP = sg->det->nLev;
  dim = sg->normal->nRow;
  sym = (dim + 1) * dim / 2;

  FMF_SetFirst( traction );
/*   fmf_print( traction, stdout, 0 ); */

  fmf_createAlloc( &trac, 1, 1, traction->nCol, nEP );
  fmf_createAlloc( &tracQP, 1, nQP, traction->nCol, 1 );
  fmf_createAlloc( &outQP, 1, nQP, dim * nFP, 1 );

  if (traction->nCol == 1) { // Pressure.
    fmf_createAlloc( &pn, 1, nQP, dim, 1 );

    for (ii = 0; ii < elList_nRow; ii++) {
      iel = elList[ii];

      FMF_SetCell( out, ii );
      FMF_SetCell( sg->normal, iel );
      FMF_SetCell( sg->det, iel );

      ele_extractNodalValuesDBD( trac, traction, conn + nEP * iel );
      bf_act( tracQP, gbf, trac );
      fmf_mulAB_nn( pn, sg->normal, tracQP );
      bf_actt_c1( outQP, bf, pn );

      fmf_sumLevelsMulF( out, outQP, sg->det->val );
      ERR_CheckGo( ret );
    }

  } else if (traction->nCol == dim) { // Traction vector.

    for (ii = 0; ii < elList_nRow; ii++) {
      iel = elList[ii];

      FMF_SetCell( out, ii );
      FMF_SetCell( sg->normal, iel );
      FMF_SetCell( sg->det, iel );

      ele_extractNodalValuesDBD( trac, traction, conn + nEP * iel );
      bf_act( tracQP, gbf, trac );
      bf_actt_c1( outQP, bf, tracQP );
      fmf_sumLevelsMulF( out, outQP, sg->det->val );
      ERR_CheckGo( ret );
    }

  } else if (traction->nCol == sym) { // Traction tensor.
    fmf_createAlloc( &stn, 1, nQP, dim, 1 );

    for (ii = 0; ii < elList_nRow; ii++) {
      iel = elList[ii];

      FMF_SetCell( out, ii );
      FMF_SetCell( sg->normal, iel );
      FMF_SetCell( sg->det, iel );

      ele_extractNodalValuesDBD( trac, traction, conn + nEP * iel );
      bf_act( tracQP, gbf, trac );
      geme_mulAVSB3( stn, tracQP, sg->normal );
      bf_actt_c1( outQP, bf, stn );

      fmf_sumLevelsMulF( out, outQP, sg->det->val );
      ERR_CheckGo( ret );
    }

  } else {
    errput( ErrHead "ERR_Switch\n" );
  }

 end_label:
  fmf_freeDestroy( &trac ); 
  fmf_freeDestroy( &tracQP ); 
  fmf_freeDestroy( &outQP ); 
  if (traction->nCol == 1) {
    fmf_freeDestroy( &pn ); 
  } else if (traction->nCol == sym) {
    fmf_freeDestroy( &stn ); 
  }

  return( ret );
}

/*       fmf_print( trac, stdout, 0 ); */
/*       fmf_print( tracQP, stdout, 0 ); */
/*       fmf_print( pn, stdout, 0 ); */
/*       fmf_print( stn, stdout, 0 ); */
/*       fmf_print( outQP, stdout, 0 ); */
/*       fmf_print( sg->normal, stdout, 0 ); */
/*       fmf_print( sg->det, stdout, 0 ); */
/*       sys_pause(); */
