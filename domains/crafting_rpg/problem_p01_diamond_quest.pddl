(define (problem crafting-rpg-diamond-quest)
  (:domain crafting-rpg)
  (:objects
    steve - agent
    spawn_clearing forest rocky_hills cavern_entrance deep_abyss - location
    item_wood - wood
    item_planks - planks
    item_wood_pick - wooden_pickaxe
    item_stone - stone
    item_coal - coal
    item_iron_ore - iron_ore
    item_iron_ingot - iron_ingot
    item_iron_pick - iron_pickaxe
    item_diamond - diamond
  )
  (:init
    (at steve spawn_clearing)

    ;; Topology layout
    (adjacent spawn_clearing forest)
    (adjacent forest spawn_clearing)

    (adjacent spawn_clearing rocky_hills)
    (adjacent rocky_hills spawn_clearing)

    (adjacent rocky_hills cavern_entrance)
    (adjacent cavern_entrance rocky_hills)

    (adjacent cavern_entrance deep_abyss)
    (adjacent deep_abyss cavern_entrance)

    ;; Resource nodes
    (resource-at item_wood forest)
    (resource-at item_stone rocky_hills)
    (resource-at item_coal cavern_entrance)
    (resource-at item_iron_ore cavern_entrance)
    (resource-at item_diamond deep_abyss)
  )
  (:goal
    (has-item steve item_diamond)
  )
)
