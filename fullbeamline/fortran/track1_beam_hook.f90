!--------------------------------------------------------------------------
!--------------------------------------------------------------------------
!--------------------------------------------------------------------------
!+
! Subroutine track1_beam_hook (beam_start, lat, ele, beam_end, err, centroid, direction)
!
! Routine that can be customized for tracking a beam through a single element.
!
! Input:
!   beam_start   -- Beam_struct: Starting beam position.
!   lat          -- lat_struct: Lattice containing element to be tracked through.
!   ele          -- Ele_struct: Element to track through.
!   centroid(0:) -- coord_struct, optional: Approximate centroid orbit. Only needed if CSR is on.
!                     Hint: Calculate this before beam tracking by tracking a single particle.
!   direction    -- integer, optional: +1 (default) -> Track forward, -1 -> Track backwards.
!
! Output:
!   beam_end    -- beam_struct: Ending beam position.
!   err         -- Logical: Set true if there is an error.
!                    EG: Too many particles lost for a CSR calc.
!   finished    -- logical: When set True, the standard track1_beam code will not be called.
!-

subroutine track1_beam_hook (beam_start, lat, ele, beam_end, err, centroid, direction, finished)

use bmad, dummy => track1_beam_hook

implicit none

type (beam_struct) beam_start
type (beam_struct) :: beam_end
type (lat_struct) :: lat
type (ele_struct) ele
type (coord_struct), optional :: centroid(0:)

integer, optional :: direction
logical err, finished

integer :: fileno, ios, n_particles, i, j, error_indicator
real(rp) :: q_total, p_reference, e_reference, q_particle, vec(6), t

! do nothing if the element is not a custom element
if (ele%key /= custom$) then
  finished = .false.
  return
endif

! multi-bunch tracking is not supported
if (size(beam_start%bunch) /= 1) then
  print *, 'UCLA Bmad Error: Bunch tracking not supported'
  stop 'error'
endif

! open parameters file
fileno = lunget()
open (unit = fileno, file = '__parameters', iostat = ios, status = 'replace')
if (ios /= 0) then
  print *, 'UCLA Bmad Error: Unable to create parameters file'
  stop 'error'
endif

! write parameters to file
if (trim(attribute_name(ele, custom_attribute1$)) /= '!NULL') then
 write (fileno, *, iostat=ios) attribute_name(ele, custom_attribute1$), ' = ', ele%value(custom_attribute1$)
endif
if (ios /= 0) then
  print *, 'UCLA Bmad Error: Failed to write to parameters file'
  stop 'error'
endif
if (trim(attribute_name(ele, custom_attribute2$)) /= '!NULL') then
 write (fileno, *, iostat=ios) attribute_name(ele, custom_attribute2$), ' = ', ele%value(custom_attribute2$)
endif
if (ios /= 0) then
  print *, 'UCLA Bmad Error: Failed to write to parameters file'
  stop 'error'
endif
if (trim(attribute_name(ele, custom_attribute3$)) /= '!NULL') then
 write (fileno, *, iostat=ios) attribute_name(ele, custom_attribute3$), ' = ', ele%value(custom_attribute3$)
endif
if (ios /= 0) then
  print *, 'UCLA Bmad Error: Failed to write to parameters file'
  stop 'error'
endif
if (trim(attribute_name(ele, custom_attribute4$)) /= '!NULL') then
 write (fileno, *, iostat=ios) attribute_name(ele, custom_attribute4$), ' = ', ele%value(custom_attribute4$)
endif
if (ios /= 0) then
  print *, 'UCLA Bmad Error: Failed to write to parameters file'
  stop 'error'
endif
if (trim(attribute_name(ele, custom_attribute5$)) /= '!NULL') then
 write (fileno, *, iostat=ios) attribute_name(ele, custom_attribute5$), ' = ', ele%value(custom_attribute5$)
endif
if (ios /= 0) then
  print *, 'UCLA Bmad Error: Failed to write to parameters file'
  stop 'error'
endif

! close parameters file
close (fileno, iostat=ios)
if (ios /= 0) then
  print *, 'UCLA Bmad Error: Failed to close parameters file'
  stop 'error'
endif

! call python script
call system_command('fullbeamline --callgpt')

! open particles file
fileno = lunget()
open (unit = fileno, file = '__particles', iostat = ios, status = 'old')
if (ios /= 0) then
  print *, 'UCLA Bmad Error: Failed to open particles file'
  stop 'error'
endif

! read error indicator from particle file
read (unit = fileno, fmt = *, iostat = ios) error_indicator
if (ios /= 0) then
  print *, 'UCLA Bmad Error: Error while reading particles file'
  stop 'error'
endif

! check error indicator
if (error_indicator == 1) then
  do i = 1, size(beam_end%bunch)
    do j = 1, size(beam_end%bunch(i)%particle)
      beam_end%bunch(i)%particle(j)%vec(1) = 999999999.0
    end do
  end do
  finished = .true.
  err = .true.
  return
endif


! read number of particles, total charge, and reference momentum from start of
! particles file
read (unit = fileno, fmt = *, iostat = ios) q_total, p_reference, n_particles
if (ios /= 0) then
  print *, 'UCLA Bmad Error: Error while reading particles file'
  stop 'error'
endif

! the number of particles may have changed, so resize the beam
call reallocate_beam(beam_end, 1, n_particles)

! compute the reference energy from the reference momentum
call convert_pc_to(p_reference, electron$, E_tot=e_reference)

! set the reference energy and momenta of the lattice element and do bookkeeping
! Note that E_tot and p0c are not changed, but by setting the flags it causes
! them to be recalculated, and since they depend on delta_e, the recalculated
! value will be the new correct value
ele%value(delta_e$) = e_reference - ele%value(E_tot_start$)
call set_flags_for_changed_attribute(ele, ele%value(delta_e$))
call set_flags_for_changed_attribute(ele, ele%value(E_tot$))
call set_flags_for_changed_attribute(ele, ele%value(p0c$))
call lattice_bookkeeper(lat)

! setup bunch
beam_end%bunch(1)%charge_tot = q_total
beam_end%bunch(1)%charge_live = q_total
beam_end%bunch(1)%z_center = 0.0
beam_end%bunch(1)%t_center = 0.0
beam_end%bunch(1)%ix_ele = ele%ix_ele
beam_end%bunch(1)%ix_bunch = 1
beam_end%bunch(1)%n_live = n_particles

! compute the charge per particle
q_particle = q_total / n_particles

! read in each particle
do i = 1, n_particles

  ! read numbers from particles file
  read (unit = fileno, fmt = *, iostat = ios) vec, t
  if (ios /= 0) then
    print *, 'UCLA Bmad Error: Error while reading particles file'
    stop 'error'
  endif

  ! initialize particle
  call init_coord(beam_end%bunch(1)%particle(i), vec, ele, downstream_end$, electron$, 1, shift_vec6 = .false.)

  ! set the time
  beam_end%bunch(1)%particle(i)%t = t

  ! init_coord does not set the charge, so set it here
  beam_end%bunch(1)%particle(i)%charge = q_particle

end do

! close particles file
close (unit = fileno, iostat = ios)
if (ios /= 0) then
  print *, 'UCLA Bmad Error: Unable to delete particles file'
  stop 'error'
endif

! no need to do regular tracking
finished = .true.

! errors in this subroutine are fail-fast, so they terminate the program rather
! than returning an error code to the calling subroutine. This means the
! returned error code is always that there is no error
err = .false.

end subroutine
