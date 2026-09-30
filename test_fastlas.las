#modeh(pick(var(block))).
#modeb(clear(var(block))).
#modeb(on_table(var(block))).
#modeb(hand_empty).

#constant(block, a).
#constant(block, b).
#constant(block, c).
#constant(block, d).

#pos(eg1, {pick(a)}, {}, {
  clear(a).
  on_table(a).
  hand_empty.
}).

#pos(eg2, {pick(b)}, {}, {
  clear(b).
  on_table(b).
  hand_empty.
}).

#pos(eg3, {}, {pick(c)}, {
  on_table(c).
  hand_empty.
}).

#pos(eg4, {}, {pick(d)}, {
  clear(d).
  on_table(d).
}).
