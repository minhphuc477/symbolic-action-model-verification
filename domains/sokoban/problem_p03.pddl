; Sokoban problem instance p03 — 5x5 Grid with Central Wall Barrier
(define (problem sokoban-p03)
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
    ; Horizontal adjacencies
    (adjacent l11 l12 right) (adjacent l12 l11 left)
    (adjacent l12 l13 right) (adjacent l13 l12 left)
    (adjacent l13 l14 right) (adjacent l14 l13 left)
    (adjacent l14 l15 right) (adjacent l15 l14 left)

    (adjacent l21 l22 right) (adjacent l22 l21 left)
    (adjacent l22 l23 right) (adjacent l23 l22 left)
    (adjacent l23 l24 right) (adjacent l24 l23 left)
    (adjacent l24 l25 right) (adjacent l25 l24 left)

    (adjacent l31 l32 right) (adjacent l32 l31 left)
    (adjacent l32 l33 right) (adjacent l33 l32 left)
    (adjacent l33 l34 right) (adjacent l34 l33 left)
    (adjacent l34 l35 right) (adjacent l35 l34 left)

    (adjacent l41 l42 right) (adjacent l42 l41 left)
    (adjacent l42 l43 right) (adjacent l43 l42 left)
    (adjacent l43 l44 right) (adjacent l44 l43 left)
    (adjacent l44 l45 right) (adjacent l45 l44 left)

    (adjacent l51 l52 right) (adjacent l52 l51 left)
    (adjacent l52 l53 right) (adjacent l53 l52 left)
    (adjacent l53 l54 right) (adjacent l54 l53 left)
    (adjacent l54 l55 right) (adjacent l55 l54 left)

    ; Vertical adjacencies
    (adjacent l11 l21 down) (adjacent l21 l11 up)
    (adjacent l21 l31 down) (adjacent l31 l21 up)
    (adjacent l31 l41 down) (adjacent l41 l31 up)
    (adjacent l41 l51 down) (adjacent l51 l41 up)

    (adjacent l12 l22 down) (adjacent l22 l12 up)
    (adjacent l22 l32 down) (adjacent l32 l22 up)
    (adjacent l32 l42 down) (adjacent l42 l32 up)
    (adjacent l42 l52 down) (adjacent l52 l42 up)

    (adjacent l13 l23 down) (adjacent l23 l13 up)
    (adjacent l23 l33 down) (adjacent l33 l23 up)
    (adjacent l33 l43 down) (adjacent l43 l33 up)
    (adjacent l43 l53 down) (adjacent l53 l43 up)

    (adjacent l14 l24 down) (adjacent l24 l14 up)
    (adjacent l24 l34 down) (adjacent l34 l24 up)
    (adjacent l34 l44 down) (adjacent l44 l34 up)
    (adjacent l44 l54 down) (adjacent l54 l44 up)

    (adjacent l15 l25 down) (adjacent l25 l15 up)
    (adjacent l25 l35 down) (adjacent l35 l25 up)
    (adjacent l35 l45 down) (adjacent l45 l35 up)
    (adjacent l45 l55 down) (adjacent l55 l45 up)

    ; Initial Positions
    (at-player l21)
    (at-box l22)

    ; Clear cells — Note: l23 and l33 are WALL obstacles (NOT CLEAR)
    (clear l11) (clear l12) (clear l13) (clear l14) (clear l15)
    (clear l24) (clear l25)
    (clear l31) (clear l32) (clear l34) (clear l35)
    (clear l41) (clear l42) (clear l43) (clear l44) (clear l45)
    (clear l51) (clear l52) (clear l53) (clear l54) (clear l55)
  )
  (:goal (and
    (at-box l25)
  ))
)
