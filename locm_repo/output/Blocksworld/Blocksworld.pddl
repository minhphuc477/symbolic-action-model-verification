(define  (domain Blocksworld)
  (:requirements :typing)
  (:types zero b1)
  (:predicates
    (zero_fsm0_state0)
    (zero_fsm0_state1 ?v0 - b1)
    (b1_fsm0_state0)
    (b1_fsm0_state1 ?v0 - zero)
    (b1_fsm0_state2 ?v1 - zero ?v2 - b1)
    (b1_fsm1_state0 ?v0 - zero)
    (b1_fsm1_state1)
    (b1_fsm1_state2 ?v1 - zero ?v2 - b1)
    (b1_fsm2_state0 ?v7 - b1 ?v11 - zero)
    (b1_fsm2_state1 ?v0 - zero)
    (b1_fsm2_state2 ?v1 - b1 ?v2 - zero)
  )
  (:action  unstack   :parameters  (?zero - zero ?b2 - b1 ?b1 - b1 )
   :precondition   (and
        (b1_fsm0_state2 ?v1 - zero ?v2 - b1)
        (b1_fsm1_state2 ?v1 - zero ?v2 - b1)
        (b1_fsm2_state0 ?v7 - b1 ?v11 - zero)
        (b1_fsm2_state2 ?v1 - b1 ?v2 - zero)
   )
   :effect   (and
        (b1_fsm0_state1 ?v0 - zero)
        (b1_fsm1_state0 ?v0 - zero)
        (b1_fsm2_state2 ?v1 - b1 ?v2 - zero)
        (b1_fsm2_state1 ?v0 - zero)
  ))

  (:action  stack   :parameters  (?zero - zero ?b1 - b1 ?b3 - b1 )
   :precondition   (and
        (b1_fsm0_state1 ?v0 - zero)
        (b1_fsm1_state0 ?v0 - zero)
        (b1_fsm2_state1 ?v0 - zero)
        (b1_fsm2_state2 ?v1 - b1 ?v2 - zero)
   )
   :effect   (and
        (b1_fsm0_state2 ?v1 - zero ?v2 - b1)
        (b1_fsm1_state2 ?v1 - zero ?v2 - b1)
        (b1_fsm2_state2 ?v1 - b1 ?v2 - zero)
        (b1_fsm2_state0 ?v7 - b1 ?v11 - zero)
  ))

  (:action  putdown   :parameters  (?zero - zero ?b2 - b1 )
   :precondition   (and
        (zero_fsm0_state1 ?v0 - b1)
        (b1_fsm1_state0 ?v0 - zero)
   )
   :effect   (and
        (zero_fsm0_state0)
        (b1_fsm1_state1)
  ))

  (:action  pick   :parameters  (?zero - zero ?b1 - b1 )
   :precondition   (and
        (zero_fsm0_state0)
        (b1_fsm0_state0)
   )
   :effect   (and
        (zero_fsm0_state1 ?v0 - b1)
        (b1_fsm0_state1 ?v0 - zero)
  ))

)
