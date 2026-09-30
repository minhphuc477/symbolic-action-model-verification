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
	:precondition (and (ontable ?o1) (clear ?o1))
	:effect (and 
		(not (ontable ?o1))
		(not (clear ?o1))
		(holding ?o1)

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
		(handempty )
		(clear ?o1)
		(not (clear ?o2))
		(not (holding ?o1))
		(on ?o1 ?o2)

	)
)

(:action unstack
	:parameters (?o1 ?o2)
	:precondition (and (handempty ) (clear ?o1) (on ?o1 ?o2))
	:effect (and 
		(not (handempty ))
		(not (clear ?o1))
		(clear ?o2)
		(holding ?o1)
		(not (on ?o1 ?o2))

	)
))
