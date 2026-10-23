; Blocksworld problem p02 — 4 blocks, reverse stack
(define (problem bw-p02)
  (:domain blocksworld)
  (:objects a b c d)
  (:init
    (on a b)
    (on b c)
    (on c d)
    (ontable d)
    (clear a)
    (handempty)
  )
  (:goal (and
    (on d c)
    (on c b)
    (on b a)
    (ontable a)
  ))
)
