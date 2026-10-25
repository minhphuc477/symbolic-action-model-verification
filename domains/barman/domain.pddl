(define (domain barman)
  (:requirements :strips :typing)
  (:types hand level beverage dispenser container - object
          ingredient cocktail - beverage
          shot shaker - container)
  (:predicates
    (ontable ?c - container)
    (holding ?h - hand ?c - container)
    (handempty ?h - hand)
    (empty ?c - container)
    (contains ?c - container ?b - beverage)
    (clean ?c - container)
    (used ?c - container ?b - beverage)
    (dispenses ?d - dispenser ?i - ingredient)
    (shaker-empty-level ?s - shaker ?l - level)
    (shaker-level ?s - shaker ?l - level)
    (next ?l1 ?l2 - level)
    (unshaked ?s - shaker)
    (shaked ?s - shaker)
    (cocktail-part1 ?c - cocktail ?i - ingredient)
    (cocktail-part2 ?c - cocktail ?i - ingredient)
  )

  (:action grasp
    :parameters (?h - hand ?c - container)
    :precondition (and (ontable ?c) (handempty ?h))
    :effect (and (not (ontable ?c)) (not (handempty ?h)) (holding ?h ?c))
  )

  (:action leave
    :parameters (?h - hand ?c - container)
    :precondition (holding ?h ?c)
    :effect (and (not (holding ?h ?c)) (handempty ?h) (ontable ?c))
  )

  (:action fill-shot
    :parameters (?s - shot ?i - ingredient ?h1 ?h2 - hand ?d - dispenser)
    :precondition (and (holding ?h1 ?s) (handempty ?h2) (dispenses ?d ?i) (empty ?s) (clean ?s))
    :effect (and (not (empty ?s)) (contains ?s ?i) (not (clean ?s)) (used ?s ?i))
  )

  (:action clean-shot
    :parameters (?s - shot ?h1 ?h2 - hand)
    :precondition (and (holding ?h1 ?s) (handempty ?h2) (empty ?s))
    :effect (and (clean ?s))
  )

  (:action pour-shot-to-empty-shaker
    :parameters (?s - shot ?i - ingredient ?sh - shaker ?h - hand ?l ?l1 - level)
    :precondition (and (holding ?h ?s) (contains ?s ?i) (shaker-empty-level ?sh ?l) (next ?l ?l1) (empty ?sh))
    :effect (and (not (contains ?s ?i)) (empty ?s) (not (shaker-empty-level ?sh ?l)) (shaker-level ?sh ?l1) (not (empty ?sh)) (unshaked ?sh))
  )

  (:action shake
    :parameters (?c - cocktail ?i1 ?i2 - ingredient ?sh - shaker ?h1 ?h2 - hand ?l - level)
    :precondition (and (holding ?h1 ?sh) (handempty ?h2) (shaker-level ?sh ?l) (unshaked ?sh) (cocktail-part1 ?c ?i1) (cocktail-part2 ?c ?i2))
    :effect (and (not (unshaked ?sh)) (shaked ?sh) (not (contains ?sh ?i1)) (not (contains ?sh ?i2)) (contains ?sh ?c))
  )

  (:action pour-shaker-to-shot
    :parameters (?b - beverage ?s - shot ?sh - shaker ?h1 ?h2 - hand ?l ?l1 - level)
    :precondition (and (holding ?h1 ?sh) (holding ?h2 ?s) (shaked ?sh) (contains ?sh ?b) (empty ?s) (shaker-level ?sh ?l) (next ?l1 ?l))
    :effect (and (not (contains ?sh ?b)) (contains ?s ?b) (not (shaker-level ?sh ?l)) (shaker-level ?sh ?l1))
  )

  (:action clean-shaker
    :parameters (?sh - shaker ?h1 ?h2 - hand)
    :precondition (and (holding ?h1 ?sh) (handempty ?h2) (empty ?sh))
    :effect (and (clean ?sh))
  )
)
