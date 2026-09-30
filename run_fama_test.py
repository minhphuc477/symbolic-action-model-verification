from meta_planning import dataset, LearningTask

domain = 'blocks'
m_ref = dataset.load_model(domain)
m = m_ref.observe(precondition_observability=0, effect_observability=0)
T = dataset.load_trajectories(domain, select=range(1))
O = [t.observe(0.5, action_observability=1, goal_observability=1) for t in T]
task = LearningTask(m, O)
sol = task.learn()
print("Solution status:", sol.solution_found)
print("LEARNED PDDL DOMAIN MODEL:")
print(sol.learned_model)


