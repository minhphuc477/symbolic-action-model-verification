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
	:precondition (and (clear ?o1))
	:effect (and 
		(not (clear ?o1))
		(holding ?o1)
		(handempty )
		(ontable ?o1)

	)
)

(:action put-down
	:parameters (?o1)
	:precondition (and (holding ?o1))
	:effect (and 
		(clear ?o1)
		(not (holding ?o1))
		(handempty )
		(ontable ?o1)

	)
)

(:action stack
	:parameters (?o1 ?o2)
	:precondition (and (holding ?o1) (clear ?o2))
	:effect (and 
		(handempty )
		(not (clear ?o2))
		(not (holding ?o1))
		(on ?o1 ?o2)
		(clear ?o1)

	)
)

(:action unstack
	:parameters (?o1 ?o2)
	:precondition (and (clear ?o1) (handempty ) (on ?o1 ?o2))
	:effect (and 
		(not (handempty ))
		(clear ?o2)
		(holding ?o1)
		(not (on ?o1 ?o2))
		(not (clear ?o1))

	)
))
