;; Dungeon Escape PDDL Domain (RPG & Adventure Game Mechanics)
;; The player must pick up a key to unlock a locked door and reach the exit.
;; Bottleneck: You cannot pass through or unlock a door without holding the key.
(define (domain dungeon-escape)
  (:requirements :strips :typing)
  (:types
    location thing - object
    player key - thing
  )
  (:predicates
    (at ?obj - thing ?loc - location)
    (has-key ?p - player ?k - key)
    (door-locked ?loc - location)
    (door-open ?loc - location)
    (adjacent ?from - location ?to - location)
  )

  (:action move
    :parameters (?p - player ?from - location ?to - location)
    :precondition (and
      (at ?p ?from)
      (adjacent ?from ?to)
      (not (door-locked ?to))
    )
    :effect (and
      (at ?p ?to)
      (not (at ?p ?from))
    )
  )

  (:action pickup-key
    :parameters (?p - player ?k - key ?loc - location)
    :precondition (and
      (at ?p ?loc)
      (at ?k ?loc)
    )
    :effect (and
      (has-key ?p ?k)
      (not (at ?k ?loc))
    )
  )

  (:action unlock-door
    :parameters (?p - player ?k - key ?door - location ?from - location)
    :precondition (and
      (at ?p ?from)
      (adjacent ?from ?door)
      (door-locked ?door)
    )
    :effect (and
      (door-open ?door)
      (not (door-locked ?door))
    )
  )
)
