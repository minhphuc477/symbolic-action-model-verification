(define (problem pitch-black-p02)
  (:domain pitch-black)
  (:objects
    loc_0_0 loc_0_1 loc_0_2
    loc_1_0 loc_1_1 loc_1_2 - location
  )
  (:init
    (at-player loc_0_0)

    ;; Direct path cell loc_0_1 is DARK (Hazard!)
    ;; Safe detour is row 1: loc_1_0 -> loc_1_1 -> loc_1_2 -> loc_0_2
    (is-light-on loc_0_0)
    ;; loc_0_1 is NOT lit! (Dark hazard)
    (is-light-on loc_0_2)
    (is-light-on loc_1_0)
    (is-light-on loc_1_1)
    (is-light-on loc_1_2)

    ;; Adjacencies
    (adjacent loc_0_0 loc_0_1) (adjacent loc_0_1 loc_0_0)
    (adjacent loc_0_1 loc_0_2) (adjacent loc_0_2 loc_0_1)

    (adjacent loc_1_0 loc_1_1) (adjacent loc_1_1 loc_1_0)
    (adjacent loc_1_1 loc_1_2) (adjacent loc_1_2 loc_1_1)

    (adjacent loc_0_0 loc_1_0) (adjacent loc_1_0 loc_0_0)
    (adjacent loc_0_1 loc_1_1) (adjacent loc_1_1 loc_0_1)
    (adjacent loc_0_2 loc_1_2) (adjacent loc_1_2 loc_0_2)
  )
  (:goal
    (at-player loc_0_2)
  )
)
