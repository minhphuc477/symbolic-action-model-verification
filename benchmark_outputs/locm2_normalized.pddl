(define  (domain Blocksworld)
  (:requirements :typing)
  (:types object)
  (:predicates
    (on ?o1 - object ?o2 - object)
    (ontable ?o1 - object)
    (clear ?o1 - object)
    (handempty)
    (holding ?o1 - object)
  )
  (:action stack
   :parameters (?o1 - object ?o2 - object ?o3 - object)
   :precondition   (and
        (holding ?v0)
        (on ?v1 ?o2)
        (clear ?v0)
        (clear ?v2)
        (holding ?v1)
   )
   :effect   (and
        (handempty)
        (ontable ?o1)
        (ontable ?v1)
        (on ?v0 ?v3)
        (clear ?v2)
  ))

  (:action pick
   :parameters (?o1 - object ?o2 - object)
   :precondition   (and
        (handempty)
        (clear ?o1)
        (clear ?v2)
   )
   :effect   (and
        (holding ?v0)
        (clear ?v0)
        (holding ?v1)
  ))

  (:action unstack
   :parameters (?o1 - object ?o2 - object ?o3 - object)
   :precondition   (and
        (clear ?o1)
        (ontable ?v1)
        (on ?v0 ?v3)
   )
   :effect   (and
        (b3_fsm0_state3 ?v0)
        (clear ?v0)
        (clear ?v2)
  ))

  (:action putdown
   :parameters (?o1 - object ?o2 - object)
   :precondition   (and
        (b3_fsm0_state3 ?v0)
   )
   :effect   (and
        (on ?v1 ?o2)
  ))

)
