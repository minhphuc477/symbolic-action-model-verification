(define (domain Blocksworld)
  (:requirements :strips)
  (:predicates
    (on ?o1 ?o2)
    (ontable ?o1)
    (clear ?o1)
    (handempty)
    (holding ?o1)
  )

  (:action pick-up
    :parameters (?o1)
    :precondition (and (clear ?o1) (handempty) (ontable ?o1))
    :effect (and)
  )

  (:action put-down
    :parameters (?o1)
    :precondition (and (holding ?o1))
    :effect (and)
  )

  (:action stack
    :parameters (?o1 ?o2)
    :precondition (and (clear ?o2) (holding ?o1))
    :effect (and)
  )

  (:action unstack
    :parameters (?o1 ?o2)
    :precondition (and (clear ?o1) (handempty) (on ?o1 ?o2))
    :effect (and)
  )

)
