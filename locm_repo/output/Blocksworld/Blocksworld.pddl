(define  (domain Blocksworld)
  (:requirements :typing)
  (:types zero b4)
  (:predicates
    (zero_fsm0_state0 ?v0 - b4)
    (zero_fsm0_state1)
    (b4_fsm0_state0 ?v0 - zero ?v3 - b4)
    (b4_fsm0_state1)
    (b4_fsm0_state2 ?v1 - zero)
    (b4_fsm1_state0)
    (b4_fsm1_state1 ?v0 - zero ?v3 - b4)
    (b4_fsm1_state2 ?v1 - zero)
    (b4_fsm2_state0 ?v4 - zero ?v6 - b4)
    (b4_fsm2_state1 ?v0 - zero)
    (b4_fsm2_state2 ?v1 - zero ?v13 - b4)
  )
  (:action  unstack   :parameters  (?zero - zero ?b2 - b4 ?b1 - b4 )
   :precondition   (and
        (zero_fsm0_state1)
        (b4_fsm0_state0 ?v0 - zero ?v3 - b4)
        (b4_fsm1_state1 ?v0 - zero ?v3 - b4)
        (b4_fsm2_state0 ?v4 - zero ?v6 - b4)
        (b4_fsm2_state2 ?v1 - zero ?v13 - b4)
   )
   :effect   (and
        (zero_fsm0_state0 ?v0 - b4)
        (b4_fsm0_state2 ?v1 - zero)
        (b4_fsm1_state2 ?v1 - zero)
        (b4_fsm2_state2 ?v1 - zero ?v13 - b4)
        (b4_fsm2_state1 ?v0 - zero)
  ))

  (:action  putdown   :parameters  (?zero - zero ?b2 - b4 )
   :precondition   (and
        (zero_fsm0_state0 ?v0 - b4)
        (b4_fsm1_state2 ?v1 - zero)
        (b4_fsm2_state1 ?v0 - zero)
   )
   :effect   (and
        (zero_fsm0_state1)
        (b4_fsm1_state0)
        (b4_fsm2_state2 ?v1 - zero ?v13 - b4)
  ))

  (:action  stack   :parameters  (?zero - zero ?b1 - b4 ?b3 - b4 )
   :precondition   (and
        (b4_fsm0_state2 ?v1 - zero)
        (b4_fsm1_state2 ?v1 - zero)
        (b4_fsm2_state2 ?v1 - zero ?v13 - b4)
   )
   :effect   (and
        (b4_fsm0_state0 ?v0 - zero ?v3 - b4)
        (b4_fsm1_state1 ?v0 - zero ?v3 - b4)
        (b4_fsm2_state0 ?v4 - zero ?v6 - b4)
  ))

  (:action  pick   :parameters  (?zero - zero ?b1 - b4 )
   :precondition   (and
        (b4_fsm0_state1)
   )
   :effect   (and
        (b4_fsm0_state2 ?v1 - zero)
  ))

)
