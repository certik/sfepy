/*!
  @par Revision history:
  - 31.03.2008, c
*/
#ifndef _TERMSBIOT_H_
#define _TERMSBIOT_H_

#include "common.h"
BEGIN_C_DECLS

#include "fmfield.h"
#include "geometry.h"

int32 dw_biot_grad( FMField *out, float64 coef, FMField *pressure_qp,
		    FMField *bf, FMField *mtxD, VolumeGeometry *vg,
		    int32 *elList, int32 elList_nRow,
		    int32 isDiff );

int32 dw_biot_div( FMField *out, float64 coef, FMField *strain,
		   FMField *bf, FMField *mtxD, VolumeGeometry *vg,
		   int32 *elList, int32 elList_nRow,
		   int32 isDiff );

int32 d_biot_div( FMField *out, float64 coef, FMField *state, FMField *strain,
		  FMField *mtxD, VolumeGeometry *vg,
		  int32 *elList, int32 elList_nRow );

END_C_DECLS

#endif /* Header */
