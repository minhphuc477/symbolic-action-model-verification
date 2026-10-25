(define (domain rover)
  (:requirements :strips :typing)
  (:types rover waypoint store camera mode lander objective - object)
  (:predicates
    (can_traverse ?r - rover ?x - waypoint ?y - waypoint)
    (at ?r - rover ?w - waypoint)
    (at_lander ?l - lander ?w - waypoint)
    (store_of ?s - store ?r - rover)
    (empty ?s - store)
    (full ?s - store)
    (at_soil_sample ?w - waypoint)
    (at_rock_sample ?w - waypoint)
    (have_soil_analysis ?r - rover ?w - waypoint)
    (have_rock_analysis ?r - rover ?w - waypoint)
    (communicated_soil_data ?w - waypoint)
    (communicated_rock_data ?w - waypoint)
    (visible ?w1 - waypoint ?w2 - waypoint)
  )

  (:action navigate
    :parameters (?r - rover ?from - waypoint ?to - waypoint)
    :precondition (and (can_traverse ?r ?from ?to) (at ?r ?from) (visible ?from ?to))
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )

  (:action sample_soil
    :parameters (?r - rover ?s - store ?w - waypoint)
    :precondition (and (at ?r ?w) (at_soil_sample ?w) (empty ?s) (store_of ?s ?r))
    :effect (and (not (empty ?s)) (full ?s) (have_soil_analysis ?r ?w) (not (at_soil_sample ?w)))
  )

  (:action drop_store
    :parameters (?r - rover ?s - store)
    :precondition (and (store_of ?s ?r) (full ?s))
    :effect (and (not (full ?s)) (empty ?s))
  )

  (:action communicate_soil_data
    :parameters (?r - rover ?l - lander ?w_sample - waypoint ?w_rover - waypoint ?w_lander - waypoint)
    :precondition (and (at ?r ?w_rover) (at_lander ?l ?w_lander) (have_soil_analysis ?r ?w_sample) (visible ?w_rover ?w_lander))
    :effect (and (communicated_soil_data ?w_sample))
  )
)
