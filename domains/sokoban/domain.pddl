; Sokoban PDDL domain — IPC standard (strips version)
; Source: International Planning Competition 2008 / Sokoban track
(define (domain sokoban-sequential)
  (:requirements :typing)
  (:types location direction)
  (:predicates
    (at-player ?l - location)
    (at-box ?b - location)
    (adjacent ?from - location ?to - location ?d - direction)
    (clear ?l - location)
    (goal-at ?l - location)
  )

  ;; Move player in empty cell
  (:action move
    :parameters (?player-from - location ?player-to - location ?d - direction)
    :precondition (and
      (at-player ?player-from)
      (adjacent ?player-from ?player-to ?d)
      (clear ?player-to)
    )
    :effect (and
      (at-player ?player-to)
      (not (at-player ?player-from))
    )
  )

  ;; Push box: player steps from player-from to box-at, box moves to box-to
  (:action push
    :parameters (?player-from - location ?box-at - location ?box-to - location ?d - direction)
    :precondition (and
      (at-player ?player-from)
      (at-box ?box-at)
      (adjacent ?player-from ?box-at ?d)
      (adjacent ?box-at ?box-to ?d)
      (clear ?box-to)
    )
    :effect (and
      (at-player ?box-at)
      (not (at-player ?player-from))
      (at-box ?box-to)
      (not (at-box ?box-at))
      (clear ?box-at)
      (not (clear ?box-to))
    )
  )
)
