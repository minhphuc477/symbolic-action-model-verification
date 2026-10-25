(define (problem dungeon-escape-p02-multikey)
  (:domain dungeon-escape)
  (:objects
    hero - player
    bronze_key silver_key gold_key - key
    entrance hall_west treasury_bronze gate_bronze
    hall_central treasury_silver gate_silver
    hall_east treasury_gold gate_gold
    sanctum_exit - location
  )
  (:init
    (at hero entrance)
    (at bronze_key treasury_bronze)
    (at silver_key treasury_silver)
    (at gold_key treasury_gold)

    (door-locked gate_bronze)
    (door-locked gate_silver)
    (door-locked gate_gold)

    ;; Tier 1: Bronze Sector
    (adjacent entrance hall_west)
    (adjacent hall_west entrance)

    (adjacent hall_west treasury_bronze)
    (adjacent treasury_bronze hall_west)

    (adjacent hall_west gate_bronze)
    (adjacent gate_bronze hall_west)

    ;; Tier 2: Silver Sector (behind gate_bronze)
    (adjacent gate_bronze hall_central)
    (adjacent hall_central gate_bronze)

    (adjacent hall_central treasury_silver)
    (adjacent treasury_silver hall_central)

    (adjacent hall_central gate_silver)
    (adjacent gate_silver hall_central)

    ;; Tier 3: Gold Sector (behind gate_silver)
    (adjacent gate_silver hall_east)
    (adjacent hall_east gate_silver)

    (adjacent hall_east treasury_gold)
    (adjacent treasury_gold hall_east)

    (adjacent hall_east gate_gold)
    (adjacent gate_gold hall_east)

    ;; Final Sanctum (behind gate_gold)
    (adjacent gate_gold sanctum_exit)
    (adjacent sanctum_exit gate_gold)
  )
  (:goal
    (at hero sanctum_exit)
  )
)
