#modeh(pick(var(block))).
#modeh(putdown(var(block))).
#modeh(stack(var(block), var(block))).
#modeh(unstack(var(block), var(block))).

#modeb(clear(var(block))).
#modeb(ontable(var(block))).
#modeb(holding(var(block))).
#modeb(handempty).
#modeb(on(var(block), var(block))).

#constant(block, a).
#constant(block, b).
#constant(block, c).
#constant(block, d).
#constant(block, e).

% --- 1. PICK ACTION EXAMPLES ---
#pos(p1, {pick(a)}, {}, { clear(a). ontable(a). handempty. }).
#pos(p2, {pick(b)}, {}, { clear(b). ontable(b). handempty. }).
#pos(p3, {pick(c)}, {}, { clear(c). ontable(c). handempty. }).
#pos(p4, {pick(d)}, {}, { clear(d). ontable(d). handempty. }).
#pos(p5, {pick(e)}, {}, { clear(e). ontable(e). handempty. }).

#pos(n_pick_1, {}, {pick(a)}, { ontable(a). handempty. }).
#pos(n_pick_2, {}, {pick(b)}, { clear(b). handempty. on(b, c). }).
#pos(n_pick_3, {}, {pick(c)}, { clear(c). ontable(c). holding(d). }).
#pos(n_pick_4, {}, {pick(d)}, { ontable(d). holding(a). }).
#pos(n_pick_5, {}, {pick(e)}, { clear(e). on(e, a). holding(b). }).

% --- 2. PUTDOWN ACTION EXAMPLES ---
#pos(pos_pd_1, {putdown(a)}, {}, { holding(a). }).
#pos(pos_pd_2, {putdown(b)}, {}, { holding(b). }).
#pos(pos_pd_3, {putdown(c)}, {}, { holding(c). }).
#pos(pos_pd_4, {putdown(d)}, {}, { holding(d). }).
#pos(pos_pd_5, {putdown(e)}, {}, { holding(e). }).

#pos(n_pd_1, {}, {putdown(a)}, { ontable(a). clear(a). handempty. }).
#pos(n_pd_2, {}, {putdown(b)}, { on(b, c). clear(b). handempty. }).
#pos(n_pd_3, {}, {putdown(c)}, { ontable(c). holding(a). }).
#pos(n_pd_4, {}, {putdown(d)}, { clear(d). ontable(d). handempty. }).
#pos(n_pd_5, {}, {putdown(e)}, { on(e, d). holding(b). }).

% --- 3. STACK ACTION EXAMPLES ---
#pos(pos_st_1, {stack(a, b)}, {}, { holding(a). clear(b). ontable(b). }).
#pos(pos_st_2, {stack(b, c)}, {}, { holding(b). clear(c). ontable(c). }).
#pos(pos_st_3, {stack(c, d)}, {}, { holding(c). clear(d). on(d, e). }).
#pos(pos_st_4, {stack(d, a)}, {}, { holding(d). clear(a). ontable(a). }).
#pos(pos_st_5, {stack(e, b)}, {}, { holding(e). clear(b). on(b, c). }).

#pos(n_st_1, {}, {stack(a, b)}, { holding(a). on(c, b). }).
#pos(n_st_2, {}, {stack(b, c)}, { handempty. clear(b). clear(c). ontable(b). }).
#pos(n_st_3, {}, {stack(c, d)}, { holding(a). clear(d). }).
#pos(n_st_4, {}, {stack(d, e)}, { holding(d). on(a, e). }).
#pos(n_st_5, {}, {stack(a, c)}, { ontable(a). clear(a). clear(c). handempty. }).

% --- 4. UNSTACK ACTION EXAMPLES ---
#pos(pos_ust_1, {unstack(a, b)}, {}, { on(a, b). clear(a). handempty. ontable(b). }).
#pos(pos_ust_2, {unstack(b, c)}, {}, { on(b, c). clear(b). handempty. ontable(c). }).
#pos(pos_ust_3, {unstack(c, d)}, {}, { on(c, d). clear(c). handempty. on(d, e). }).
#pos(pos_ust_4, {unstack(d, e)}, {}, { on(d, e). clear(d). handempty. ontable(e). }).
#pos(pos_ust_5, {unstack(e, a)}, {}, { on(e, a). clear(e). handempty. ontable(a). }).

#pos(n_ust_1, {}, {unstack(a, b)}, { on(a, b). on(c, a). handempty. }).
#pos(n_ust_2, {}, {unstack(b, c)}, { on(b, c). clear(b). holding(d). }).
#pos(n_ust_3, {}, {unstack(c, d)}, { ontable(c). clear(c). handempty. clear(d). }).
#pos(n_ust_4, {}, {unstack(d, a)}, { on(d, b). clear(d). handempty. }).
#pos(n_ust_5, {}, {unstack(e, c)}, { on(e, c). holding(a). }).
