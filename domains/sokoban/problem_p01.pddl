; Sokoban problem instance p01 — 5x5 level
; Player at (2,2), Box at (3,3), Goal at (1,1)
(define (problem sokoban-p01)
  (:domain sokoban-sequential)
  (:objects
    l11 l12 l13 l14 l15
    l21 l22 l23 l24 l25
    l31 l32 l33 l34 l35
    l41 l42 l43 l44 l45
    l51 l52 l53 l54 l55 - location
    up down left right - direction
  )
  (:init
    ; Player starts at l22 (row 2, col 2)
    (at-player l22)
    ; Box at l33
    (at-box l33)
    ; Adjacencies (row-major, walls are l11 border cells)
    (adjacent l22 l23 right) (adjacent l23 l22 left)
    (adjacent l22 l32 down)  (adjacent l32 l22 up)
    (adjacent l23 l33 down)  (adjacent l33 l23 up)
    (adjacent l32 l33 right) (adjacent l33 l32 left)
    (adjacent l33 l43 down)  (adjacent l43 l33 up)
    (adjacent l33 l34 right) (adjacent l34 l33 left)
    (adjacent l32 l42 down)  (adjacent l42 l32 up)
    (adjacent l43 l44 right) (adjacent l44 l43 left)
    (adjacent l34 l44 down)  (adjacent l44 l34 up)
    (adjacent l43 l42 left)  (adjacent l42 l43 right)
    ; Cells that are clear (not wall, not box, not player)
    (clear l23) (clear l32) (clear l34)
    (clear l42) (clear l43) (clear l44)
    (clear l13) (clear l14) (clear l24)
    (clear l31) (clear l41) (clear l21)
  )
  (:goal (and
    (at-box l11)
  ))
)
