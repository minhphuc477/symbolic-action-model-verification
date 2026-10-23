(define (problem dungeon-escape-p01)
  (:domain dungeon-escape)
  (:objects
    hero - player
    bronze_key - key
    room_entrance room_hallway room_treasury room_gate room_exit - location
  )
  (:init
    (at hero room_entrance)
    (at bronze_key room_treasury)
    (door-locked room_gate)

    ;; Topology connections:
    ;; entrance <-> hallway <-> treasury
    ;; hallway <-> gate <-> exit
    (adjacent room_entrance room_hallway)
    (adjacent room_hallway room_entrance)

    (adjacent room_hallway room_treasury)
    (adjacent room_treasury room_hallway)

    (adjacent room_hallway room_gate)
    (adjacent room_gate room_hallway)

    (adjacent room_gate room_exit)
    (adjacent room_exit room_gate)
  )
  (:goal
    (at hero room_exit)
  )
)
