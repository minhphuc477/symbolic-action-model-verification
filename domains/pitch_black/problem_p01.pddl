(define (problem pitch-black-p01)
  (:domain pitch-black)
  (:objects
    loc_0_0 loc_0_1 loc_0_2
    loc_1_0 loc_1_1 loc_1_2
    loc_2_0 loc_2_1 loc_2_2 - location
  )
  (:init
    (at-player loc_0_0)

    ;; Light grid: center cell loc_1_1 is DARK (hazard!)
    ;; Perimeter is illuminated
    (is-light-on loc_0_0)
    (is-light-on loc_0_1)
    (is-light-on loc_0_2)
    (is-light-on loc_1_0)
    ;; loc_1_1 is NOT lit! (Hazard)
    (is-light-on loc_1_2)
    (is-light-on loc_2_0)
    (is-light-on loc_2_1)
    (is-light-on loc_2_2)

    ;; Grid adjacencies (horizontal & vertical)
    (adjacent loc_0_0 loc_0_1) (adjacent loc_0_1 loc_0_0)
    (adjacent loc_0_1 loc_0_2) (adjacent loc_0_2 loc_0_1)
    (adjacent loc_1_0 loc_1_1) (adjacent loc_1_1 loc_1_0)
    (adjacent loc_1_1 loc_1_2) (adjacent loc_1_2 loc_1_1)
    (adjacent loc_2_0 loc_2_1) (adjacent loc_2_1 loc_2_0)
    (adjacent loc_2_1 loc_2_2) (adjacent loc_2_2 loc_2_1)

    (adjacent loc_0_0 loc_1_0) (adjacent loc_1_0 loc_0_0)
    (adjacent loc_1_0 loc_2_0) (adjacent loc_2_0 loc_1_0)
    (adjacent loc_0_1 loc_1_1) (adjacent loc_1_1 loc_0_1)
    (adjacent loc_1_1 loc_2_1) (adjacent loc_2_1 loc_1_1)
    (adjacent loc_0_2 loc_1_2) (adjacent loc_1_2 loc_0_2)
    (adjacent loc_1_2 loc_2_2) (adjacent loc_2_2 loc_1_2)
  )
  (:goal
    (at-player loc_2_2)
  )
)
