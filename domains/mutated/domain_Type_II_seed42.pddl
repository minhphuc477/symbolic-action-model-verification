(define
  (domain sokoban-sequential)
  (:requirements :typing)
  (:types location direction)
  (:predicates
    (at-player ?l - location)
    (at-box ?b - location)
    (adjacent ?from - location ?to - location ?d - direction)
    (clear ?l - location)
  )
  (:action
    move
    :parameters
    (?from - location ?to - location ?d - direction)
    :precondition
    (and
      (at-player ?from)
      (adjacent ?from ?to ?d)
      (clear ?to)
    )
    :effect
    (and
      (at-player ?to)
      (not
        (at-player ?from)
      )
      (clear ?from)
      (not
        (clear ?to)
      )
    )
  )
  (:action
    push
    :parameters
    (?p-pos - location ?b-pos - location ?b-target - location ?d - direction)
    :precondition
    (and
      (at-player ?p-pos)
      (at-box ?b-pos)
      (adjacent ?p-pos ?b-pos ?d)
      (adjacent ?b-pos ?b-target ?d)
    )
    :effect
    (and
      (at-player ?b-pos)
      (not
        (at-player ?p-pos)
      )
      (at-box ?b-target)
      (not
        (at-box ?b-pos)
      )
      (clear ?p-pos)
      (not
        (clear ?b-target)
      )
    )
  )
)
