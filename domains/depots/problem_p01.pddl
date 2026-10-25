(define (problem depot_p01)
  (:domain depot)
  (:objects
    depot0 - depot
    distributor0 - distributor
    truck0 - truck
    pallet0 pallet1 - pallet
    crate0 - crate
    hoist0 hoist1 - hoist
  )
  (:init
    (at pallet0 depot0)
    (clear crate0)
    (at pallet1 distributor0)
    (clear pallet1)
    (at truck0 depot0)
    (at hoist0 depot0)
    (available hoist0)
    (at hoist1 distributor0)
    (available hoist1)
    (at crate0 depot0)
    (on crate0 pallet0)
  )
  (:goal
    (and
      (on crate0 pallet1)
    )
  )
)
