!+
! Subroutine make_mat6_custom (ele, param, c0, c1, err_flag)
!
! Dummy routine for custom tracking.
! This routine needs to be replaced for a custom calculation.
! If not replaced, and this routine is called, this routine will generate an error message.
!
! General rule: Your code may NOT modify any argument that is not listed as
! an output agument below."
!
! Modules needed:
!   use bmad
!
! Input:
!   ele       -- Ele_struct: Element with transfer matrix
!   param     -- lat_param_struct: Parameters are needed for some elements.
!   c0        -- Coord_struct: Coordinates at the beginning of element.
!
! Output:
!   ele       -- Ele_struct: Element with transfer matrix.
!     %mat6     -- 6x6 transfer matrix.
!   c1        -- Coord_struct: Coordinates at the end of element.
!   err_flag  -- Logical: Set true if there is an error. False otherwise.
!+

subroutine make_mat6_custom (ele, param, c0, c1, err_flag)

use bmad_struct
use bmad_interface, except_dummy => make_mat6_custom

implicit none

type (ele_struct), target :: ele
type (coord_struct) :: c0, c1
type (lat_param_struct)  param

logical :: err_flag
character(32) :: r_name = 'make_mat6_custom'

! the 6x6 transfer matrix is just the identity matrix
call mat_make_unit(ele%mat6)

! the coordinates at the end of the element are the same
!c1 = c0
!c1%s = ele%s

! no errors occured (or can occur)
err_flag = .false.

end subroutine
