(define (problem logistics-c2-p1)
  (:domain logistics)
  (:objects
    city1 city2 - city
    city1-apt city2-apt - airport
    city1-pos city2-pos - location
    truck1 truck2 - truck
    plane1 - airplane
    pkg1 - package
  )
  (:init
    (in-city city1-apt city1)
    (in-city city1-pos city1)
    (in-city city2-apt city2)
    (in-city city2-pos city2)
    (at truck1 city1-pos)
    (at truck2 city2-pos)
    (at plane1 city1-apt)
    (at pkg1 city1-pos)
  )
  (:goal
    (and
      (at pkg1 city2-pos)
    )
  )
)
