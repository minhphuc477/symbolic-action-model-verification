;; Pitch Black PDDL Domain (PuzzleScript Game Mechanics)
;; The player must navigate a grid to reach the goal.
;; Hazard: Moving into an unlit cell (darkness) is fatal.
(define (domain pitch-black)
  (:requirements :strips :typing)
  (:types location)
  (:predicates
    (at-player ?loc - location)
    (is-light-on ?loc - location)
    (adjacent ?from - location ?to - location)
  )

  (:action move
    :parameters (?from - location ?to - location)
    :precondition (and
      (at-player ?from)
      (adjacent ?from ?to)
      (is-light-on ?to)
    )
    :effect (and
      (at-player ?to)
      (not (at-player ?from))
    )
  )
)
