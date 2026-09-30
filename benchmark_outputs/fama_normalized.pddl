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
		(holding ?o1)
		(not (clear ?o1))
		(not (ontable ?o1))

	)
)

(:action put-down
	:parameters (?o1)
	:precondition (and (holding ?o1))
	:effect (and 
		(not (holding ?o1))
		(ontable ?o1)
		(clear ?o1)
		(handempty )

	)
)

(:action stack
	:parameters (?o1 ?o2)
	:precondition (and (holding ?o1) (clear ?o2))
	:effect (and 
		(clear ?o1)
		(not (clear ?o2))
		(on ?o1 ?o2)
		(not (holding ?o1))
		(handempty )

	)
)

(:action unstack
	:parameters (?o1 ?o2)
	:precondition (and (on ?o1 ?o2) (clear ?o1) (handempty ))
	:effect (and 
		(not (clear ?o1))
		(clear ?o2)
		(not (on ?o1 ?o2))
		(holding ?o1)
		(not (handempty ))

	)
))
