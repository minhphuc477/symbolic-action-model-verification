(define  (domain Blocksworld)
  (:requirements :typing)
  (:types zero b3)
  (:predicates
    (zero_fsm0_state0 ?v2 - b3 ?v5 - b3)
    (zero_fsm0_state1 ?v0 - b3)
    (b3_fsm0_state0 ?v1 - zero)
    (b3_fsm0_state1)
    (b3_fsm0_state2)
    (b3_fsm0_state3 ?v0 - zero)
    (b3_fsm1_state0)
    (b3_fsm1_state1 ?v1 - zero ?v2 - b3)
    (b3_fsm1_state2 ?v0 - zero)
    (b3_fsm2_state0 ?v0 - zero ?v3 - b3)
    (b3_fsm2_state1 ?v2 - zero ?v5 - b3)
    (b3_fsm2_state2 ?v1 - zero)
  )
  (:action  stack   :parameters  (?zero - zero ?b1 - b3 ?b3 - b3 )
   :precondition   (and
        (zero_fsm0_state1 ?v0 - b3)
        (b3_fsm0_state0 ?v1 - zero)
        (b3_fsm1_state2 ?v0 - zero)
        (b3_fsm2_state1 ?v2 - zero ?v5 - b3)
        (b3_fsm2_state2 ?v1 - zero)
   )
   :effect   (and
        (zero_fsm0_state0 ?v2 - b3 ?v5 - b3)
        (b3_fsm0_state1)
        (b3_fsm1_state1 ?v1 - zero ?v2 - b3)
        (b3_fsm2_state0 ?v0 - zero ?v3 - b3)
        (b3_fsm2_state1 ?v2 - zero ?v5 - b3)
  ))

  (:action  pick   :parameters  (?zero - zero ?b1 - b3 )
   :precondition   (and
        (zero_fsm0_state0 ?v2 - b3 ?v5 - b3)
        (b3_fsm1_state0)
        (b3_fsm2_state1 ?v2 - zero ?v5 - b3)
   )
   :effect   (and
        (zero_fsm0_state1 ?v0 - b3)
        (b3_fsm1_state2 ?v0 - zero)
        (b3_fsm2_state2 ?v1 - zero)
  ))

  (:action  unstack   :parameters  (?zero - zero ?b2 - b3 ?b1 - b3 )
   :precondition   (and
        (b3_fsm0_state2)
        (b3_fsm1_state1 ?v1 - zero ?v2 - b3)
        (b3_fsm2_state0 ?v0 - zero ?v3 - b3)
   )
   :effect   (and
        (b3_fsm0_state3 ?v0 - zero)
        (b3_fsm1_state2 ?v0 - zero)
        (b3_fsm2_state1 ?v2 - zero ?v5 - b3)
  ))

  (:action  putdown   :parameters  (?zero - zero ?b2 - b3 )
   :precondition   (and
        (b3_fsm0_state3 ?v0 - zero)
   )
   :effect   (and
        (b3_fsm0_state0 ?v1 - zero)
  ))

)
