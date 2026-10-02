; Logistics PDDL domain — Mutated Type II (omitted (in-city ?to ?c) in drive-truck)
(define (domain logistics)
  (:requirements :strips :typing)
  (:types
    location city thing - object
    package vehicle - thing
    truck airplane - vehicle
    airport - location
  )
  (:predicates
    (at ?t - thing ?l - location)
    (in ?p - package ?v - vehicle)
    (in-city ?l - location ?c - city)
  )

  (:action load-truck
    :parameters (?p - package ?t - truck ?l - location)
    :precondition (and (at ?t ?l) (at ?p ?l))
    :effect (and (in ?p ?t) (not (at ?p ?l)))
  )

  (:action unload-truck
    :parameters (?p - package ?t - truck ?l - location)
    :precondition (and (at ?t ?l) (in ?p ?t))
    :effect (and (at ?p ?l) (not (in ?p ?t)))
  )

  (:action load-airplane
    :parameters (?p - package ?a - airplane ?l - location)
    :precondition (and (at ?a ?l) (at ?p ?l))
    :effect (and (in ?p ?a) (not (at ?p ?l)))
  )

  (:action unload-airplane
    :parameters (?p - package ?a - airplane ?l - location)
    :precondition (and (at ?a ?l) (in ?p ?a))
    :effect (and (at ?p ?l) (not (in ?p ?a)))
  )

  (:action drive-truck
    :parameters (?t - truck ?from - location ?to - location ?c - city)
    :precondition (and (at ?t ?from) (in-city ?from ?c))
    :effect (and (at ?t ?to) (not (at ?t ?from)))
  )

  (:action fly-airplane
    :parameters (?a - airplane ?from - airport ?to - airport)
    :precondition (and (at ?a ?from))
    :effect (and (at ?a ?to) (not (at ?a ?from)))
  )
)
