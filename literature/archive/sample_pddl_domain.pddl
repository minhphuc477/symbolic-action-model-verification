(define (domain Sokoban_PuzzleScript)
  (:requirements :strips :typing)
  (:types position object)
  (:predicates
     (at ?obj - object ?pos - position)
     (is-wall ?pos - position)
     (is-target ?pos - position)
     (has-key ?obj - object)
     (is-door-locked ?pos - position)
     (adjacent ?pos1 - position ?pos2 - position)
  )

  (:action move
     :parameters (?p - object ?from - position ?to - position)
     :precondition (and (at ?p ?from) (adjacent ?from ?to) (not (is-wall ?to)))
     :effect (and (not (at ?p ?from)) (at ?p ?to))
  )

  (:action push-box
     :parameters (?p - object ?b - object ?pfrom - position ?bfrom - position ?bto - position)
     :precondition (and (at ?p ?pfrom) (at ?b ?bfrom) (adjacent ?pfrom ?bfrom) (adjacent ?bfrom ?bto) (not (is-wall ?bto)))
     :effect (and (not (at ?p ?pfrom)) (at ?p ?bfrom) (not (at ?b ?bfrom)) (at ?b ?bto))
  )
)