(define (problem barman_p01)
  (:domain barman)
  (:objects
    hand1 hand2 - hand
    shaker1 - shaker
    shot1 shot2 - shot
    dispenser1 dispenser2 - dispenser
    ingredient1 ingredient2 - ingredient
    cocktail1 - cocktail
    l0 l1 l2 - level
  )
  (:init
    (ontable shaker1)
    (ontable shot1)
    (ontable shot2)
    (handempty hand1)
    (handempty hand2)
    (clean shaker1)
    (empty shaker1)
    (clean shot1)
    (empty shot1)
    (clean shot2)
    (empty shot2)
    (dispenses dispenser1 ingredient1)
    (dispenses dispenser2 ingredient2)
    (shaker-empty-level shaker1 l0)
    (next l0 l1)
    (next l1 l2)
    (cocktail-part1 cocktail1 ingredient1)
    (cocktail-part2 cocktail1 ingredient2)
  )
  (:goal
    (contains shot1 cocktail1)
  )
)
