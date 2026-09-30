(define (domain Blocksworld)
  (:requirements :strips :typing)
  (:types object)
  (:predicates
    (clear ?v0 - object)
    (handempty)
  )

  (:action pick
    :parameters (?v0 - object)
    :precondition (and (clear ?v0) (handempty))
    :effect (and)
  )

)