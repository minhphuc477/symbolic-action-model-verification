(define (problem rover_p01)
  (:domain rover)
  (:objects
    rover0 - rover
    waypoint0 waypoint1 waypoint2 - waypoint
    rover0store - store
    lander0 - lander
  )
  (:init
    (at rover0 waypoint0)
    (store_of rover0store rover0)
    (empty rover0store)
    (at_lander lander0 waypoint1)
    (at_soil_sample waypoint0)
    (can_traverse rover0 waypoint0 waypoint1)
    (can_traverse rover0 waypoint1 waypoint0)
    (can_traverse rover0 waypoint1 waypoint2)
    (can_traverse rover0 waypoint2 waypoint1)
    (visible waypoint0 waypoint1)
    (visible waypoint1 waypoint0)
    (visible waypoint1 waypoint2)
    (visible waypoint2 waypoint1)
    (visible waypoint0 waypoint0)
  )
  (:goal
    (communicated_soil_data waypoint0)
  )
)
