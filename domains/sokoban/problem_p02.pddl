; Sokoban problem instance p02 — 4x4 Grid with Wall Obstacle
; Goal is at l24. Box is at l22.
; Direct path rightwards: l21 (player) -> l22 (box) -> l23 (WALL!) -> l24 (goal)
; Under M_hat (omits clear ?b-target in push), agent thinks it can push box into l23!
; Ground Truth requires routing box around the wall via row 3.
(define (problem sokoban-p02)
  (:domain sokoban-sequential)
  (:objects
    l11 l12 l13 l14
    l21 l22 l23 l24
    l31 l32 l33 l34
    l41 l42 l43 l44 - location
    up down left right - direction
  )
  (:init
    ; Horizontal adjacencies
    (adjacent l11 l12 right) (adjacent l12 l11 left)
    (adjacent l12 l13 right) (adjacent l13 l12 left)
    (adjacent l13 l14 right) (adjacent l14 l13 left)

    (adjacent l21 l22 right) (adjacent l22 l21 left)
    (adjacent l22 l23 right) (adjacent l23 l22 left)
    (adjacent l23 l24 right) (adjacent l24 l23 left)

    (adjacent l31 l32 right) (adjacent l32 l31 left)
    (adjacent l32 l33 right) (adjacent l33 l32 left)
    (adjacent l33 l34 right) (adjacent l34 l33 left)

    (adjacent l41 l42 right) (adjacent l42 l41 left)
    (adjacent l42 l43 right) (adjacent l43 l42 left)
    (adjacent l43 l44 right) (adjacent l44 l43 left)

    ; Vertical adjacencies
    (adjacent l11 l21 down) (adjacent l21 l11 up)
    (adjacent l21 l31 down) (adjacent l31 l21 up)
    (adjacent l31 l41 down) (adjacent l41 l31 up)

    (adjacent l12 l22 down) (adjacent l22 l12 up)
    (adjacent l22 l32 down) (adjacent l32 l22 up)
    (adjacent l32 l42 down) (adjacent l42 l32 up)

    (adjacent l13 l23 down) (adjacent l23 l13 up)
    (adjacent l23 l33 down) (adjacent l33 l23 up)
    (adjacent l33 l43 down) (adjacent l43 l33 up)

    (adjacent l14 l24 down) (adjacent l24 l14 up)
    (adjacent l24 l34 down) (adjacent l34 l24 up)
    (adjacent l34 l44 down) (adjacent l44 l34 up)

    ; Initial Positions
    (at-player l21)
    (at-box l22)

    ; Clear cells — Note: l23 is a WALL (NOT CLEAR)
    (clear l11) (clear l12) (clear l13) (clear l14)
    ; l21 is player, l22 is box, l23 is wall obstacle
    (clear l24)
    (clear l31) (clear l32) (clear l33) (clear l34)
    (clear l41) (clear l42) (clear l43) (clear l44)
  )
  (:goal (and
    (at-box l33)
  ))
)
