(define  (domain Blocksworld)
  (:requirements :typing)
  (:types zero b2)
  (:predicates
    (zero_fsm0_state0 ?v0 - b2)
    (zero_fsm0_state1 ?v2 - b2 ?v3 - b2)
    (b2_fsm0_state0 ?v1 - zero)
    (b2_fsm0_state1)
    (b2_fsm0_state2 ?v0 - zero)
    (b2_fsm0_state3)
    (b2_fsm1_state0)
    (b2_fsm1_state1)
    (b2_fsm1_state2 ?v0 - zero)
    (b2_fsm1_state3 ?v1 - zero)
    (b2_fsm2_state0 ?v1 - zero ?v4 - b2)
    (b2_fsm2_state1 ?v6 - zero)
    (b2_fsm2_state2 ?v0 - zero ?v3 - b2)
  )
  (:action  pick   :parameters  (?zero - zero ?b1 - b2 )
   :precondition   (and
        (b2_fsm1_state2 ?v0 - zero)
   )
   :effect   (and
        (b2_fsm1_state3 ?v1 - zero)
  ))

  (:action  stack   :parameters  (?zero - zero ?b1 - b2 ?b3 - b2 )
   :precondition   (and
        (zero_fsm0_state0 ?v0 - b2)
        (b2_fsm1_state3 ?v1 - zero)
        (b2_fsm2_state1 ?v6 - zero)
        (b2_fsm2_state2 ?v0 - zero ?v3 - b2)
   )
   :effect   (and
        (zero_fsm0_state1 ?v2 - b2 ?v3 - b2)
        (b2_fsm1_state0)
        (b2_fsm2_state2 ?v0 - zero ?v3 - b2)
        (b2_fsm2_state0 ?v1 - zero ?v4 - b2)
  ))

  (:action  unstack   :parameters  (?zero - zero ?b2 - b2 ?b1 - b2 )
   :precondition   (and
        (zero_fsm0_state1 ?v2 - b2 ?v3 - b2)
        (b2_fsm0_state1)
        (b2_fsm0_state2 ?v0 - zero)
        (b2_fsm1_state1)
        (b2_fsm2_state0 ?v1 - zero ?v4 - b2)
        (b2_fsm2_state2 ?v0 - zero ?v3 - b2)
   )
   :effect   (and
        (zero_fsm0_state0 ?v0 - b2)
        (b2_fsm0_state2 ?v0 - zero)
        (b2_fsm0_state0 ?v1 - zero)
        (b2_fsm1_state2 ?v0 - zero)
        (b2_fsm2_state2 ?v0 - zero ?v3 - b2)
        (b2_fsm2_state1 ?v6 - zero)
  ))

  (:action  putdown   :parameters  (?zero - zero ?b2 - b2 )
   :precondition   (and
        (b2_fsm0_state0 ?v1 - zero)
   )
   :effect   (and
        (b2_fsm0_state3)
  ))

)
