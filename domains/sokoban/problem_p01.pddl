; Sokoban problem instance p01 — 3x3 Grid
; Player at l12, Box at l22, Target/Goal at l32
(define (problem sokoban-p01)
  (:domain sokoban-sequential)
  (:objects
    l11 l12 l13
    l21 l22 l23
    l31 l32 l33 - location
    up down left right - direction
  )
  (:init
    ; Grid connections
    (adjacent l11 l12 right) (adjacent l12 l11 left)
    (adjacent l12 l13 right) (adjacent l13 l12 left)
    (adjacent l21 l22 right) (adjacent l22 l21 left)
    (adjacent l22 l23 right) (adjacent l23 l22 left)
    (adjacent l31 l32 right) (adjacent l32 l31 left)
    (adjacent l32 l33 right) (adjacent l33 l32 left)

    (adjacent l11 l21 down) (adjacent l21 l11 up)
    (adjacent l21 l31 down) (adjacent l31 l21 up)
    (adjacent l12 l22 down) (adjacent l22 l12 up)
    (adjacent l22 l32 down) (adjacent l32 l22 up)
    (adjacent l13 l23 down) (adjacent l23 l13 up)
    (adjacent l23 l33 down) (adjacent l33 l23 up)

    ; Initial positions
    (at-player l12)
    (at-box l22)

    ; Clear cells
    (clear l11) (clear l13)
    (clear l21) (clear l23)
    (clear l31) (clear l32) (clear l33)
  )
  (:goal (and
    (at-box l32)
  ))
)
