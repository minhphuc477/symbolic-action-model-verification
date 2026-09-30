(define (domain blocks)
(:requirements :strips)
(:types object)
(:predicates
	(on ?o1 - object ?o2 - object)
	(ontable ?o1 - object)
	(clear ?o1 - object)
	(handempty )
	(holding ?o1 - object)
)

(:action pick-up
	:parameters (?o1 - object)
	:precondition (and (clear ?o1))
	:effect (and 
		(holding ?o1)
		(not (clear ?o1))
		(ontable ?o1)
		(handempty )

	)
)

(:action put-down
	:parameters (?o1 - object)
	:precondition (and (holding ?o1))
	:effect (and 
		(not (holding ?o1))
		(clear ?o1)
		(ontable ?o1)
		(handempty )

	)
)

(:action stack
	:parameters (?o1 - object ?o2 - object)
	:precondition (and (holding ?o1) (clear ?o2))
	:effect (and 
		(not (clear ?o2))
		(not (holding ?o1))
		(clear ?o1)
		(on ?o1 ?o2)
		(handempty )

	)
)

(:action unstack
	:parameters (?o1 - object ?o2 - object)
	:precondition (and (clear ?o1) (on ?o1 ?o2) (handempty ))
	:effect (and 
		(clear ?o2)
		(holding ?o1)
		(not (clear ?o1))
		(not (on ?o1 ?o2))
		(not (handempty ))

	)
))
