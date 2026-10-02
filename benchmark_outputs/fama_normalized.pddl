(define (domain blocks)
(:requirements :strips)

(:predicates
	(on ?o1 ?o2)
	(ontable ?o1)
	(clear ?o1)
	(handempty )
	(holding ?o1)
)

(:action pick-up
	:parameters (?o1)
	:precondition (and (clear ?o1) (ontable ?o1))
	:effect (and 
		(not (clear ?o1))
		(holding ?o1)
		(not (ontable ?o1))

	)
)

(:action put-down
	:parameters (?o1)
	:precondition (and (holding ?o1))
	:effect (and 
		(handempty )
		(clear ?o1)
		(not (holding ?o1))
		(ontable ?o1)

	)
)

(:action stack
	:parameters (?o1 ?o2)
	:precondition (and (clear ?o2) (holding ?o1))
	:effect (and 
		(on ?o1 ?o2)
		(not (clear ?o2))
		(clear ?o1)
		(not (holding ?o1))
		(handempty )

	)
)

(:action unstack
	:parameters (?o1 ?o2)
	:precondition (and (handempty ) (clear ?o1) (on ?o1 ?o2))
	:effect (and 
		(not (on ?o1 ?o2))
		(clear ?o2)
		(not (clear ?o1))
		(holding ?o1)
		(not (handempty ))

	)
))
