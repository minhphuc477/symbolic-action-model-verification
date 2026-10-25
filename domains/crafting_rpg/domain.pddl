;; Crafting RPG Domain (Strictly Typed Resource Dependency Tech-Tree)
(define (domain crafting-rpg)
  (:requirements :strips :typing)
  (:types
    location item agent - object
    wood planks stick stone coal iron_ore iron_ingot diamond - item
    wooden_pickaxe stone_pickaxe iron_pickaxe - item
  )
  (:predicates
    (at ?ag - agent ?loc - location)
    (has-item ?ag - agent ?it - item)
    (adjacent ?from - location ?to - location)
    (resource-at ?it - item ?loc - location)
    (has-workbench ?loc - location)
    (has-furnace ?loc - location)
  )

  (:action move
    :parameters (?ag - agent ?from - location ?to - location)
    :precondition (and
      (at ?ag ?from)
      (adjacent ?from ?to)
    )
    :effect (and
      (at ?ag ?to)
      (not (at ?ag ?from))
    )
  )

  (:action gather-wood
    :parameters (?ag - agent ?loc - location ?w - wood)
    :precondition (and
      (at ?ag ?loc)
      (resource-at ?w ?loc)
    )
    :effect (and
      (has-item ?ag ?w)
    )
  )

  (:action craft-planks
    :parameters (?ag - agent ?w - wood ?p - planks)
    :precondition (and
      (has-item ?ag ?w)
    )
    :effect (and
      (has-item ?ag ?p)
    )
  )

  (:action craft-workbench
    :parameters (?ag - agent ?loc - location ?p - planks)
    :precondition (and
      (at ?ag ?loc)
      (has-item ?ag ?p)
    )
    :effect (and
      (has-workbench ?loc)
    )
  )

  (:action craft-wooden-pickaxe
    :parameters (?ag - agent ?loc - location ?p - planks ?pick - wooden_pickaxe)
    :precondition (and
      (at ?ag ?loc)
      (has-workbench ?loc)
      (has-item ?ag ?p)
    )
    :effect (and
      (has-item ?ag ?pick)
    )
  )

  (:action mine-stone
    :parameters (?ag - agent ?loc - location ?pick - wooden_pickaxe ?st - stone)
    :precondition (and
      (at ?ag ?loc)
      (resource-at ?st ?loc)
      (has-item ?ag ?pick)
    )
    :effect (and
      (has-item ?ag ?st)
    )
  )

  (:action build-furnace
    :parameters (?ag - agent ?loc - location ?st - stone)
    :precondition (and
      (at ?ag ?loc)
      (has-workbench ?loc)
      (has-item ?ag ?st)
    )
    :effect (and
      (has-furnace ?loc)
    )
  )

  (:action gather-coal
    :parameters (?ag - agent ?loc - location ?pick - wooden_pickaxe ?c - coal)
    :precondition (and
      (at ?ag ?loc)
      (resource-at ?c ?loc)
      (has-item ?ag ?pick)
    )
    :effect (and
      (has-item ?ag ?c)
    )
  )

  (:action mine-iron-ore
    :parameters (?ag - agent ?loc - location ?pick - wooden_pickaxe ?ore - iron_ore)
    :precondition (and
      (at ?ag ?loc)
      (resource-at ?ore ?loc)
      (has-item ?ag ?pick)
    )
    :effect (and
      (has-item ?ag ?ore)
    )
  )

  (:action smelt-iron
    :parameters (?ag - agent ?loc - location ?ore - iron_ore ?c - coal ?ingot - iron_ingot)
    :precondition (and
      (at ?ag ?loc)
      (has-furnace ?loc)
      (has-item ?ag ?ore)
      (has-item ?ag ?c)
    )
    :effect (and
      (has-item ?ag ?ingot)
    )
  )

  (:action craft-iron-pickaxe
    :parameters (?ag - agent ?loc - location ?ingot - iron_ingot ?p - planks ?pick - iron_pickaxe)
    :precondition (and
      (at ?ag ?loc)
      (has-workbench ?loc)
      (has-item ?ag ?ingot)
      (has-item ?ag ?p)
    )
    :effect (and
      (has-item ?ag ?pick)
    )
  )

  (:action mine-diamond
    :parameters (?ag - agent ?loc - location ?pick - iron_pickaxe ?d - diamond)
    :precondition (and
      (at ?ag ?loc)
      (resource-at ?d ?loc)
      (has-item ?ag ?pick)
    )
    :effect (and
      (has-item ?ag ?d)
      (not (resource-at ?d ?loc))
    )
  )
)
