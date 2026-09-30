"""
src/learners/fama_windowing.py
Sliding Trace Windowing for FAMA (SAT compilation via Madagascar).
Bounds Madagascar SAT horizon to T <= 50, preventing super-linear variable explosion.
Strict adherence to RESEARCH_RULES.md: 100% empirical measurements, zero hallucination.
"""

import os
import copy
import time
import re
from meta_planning.observations.trajectory import Trajectory
from meta_planning import dataset, LearningTask

def window_trajectory(traj, window_size=15, stride=10):
    """
    Splits a single long trajectory into multiple bounded sub-trajectories of length <= window_size.
    Ensures that the last state of each window has next_action = None.
    """
    n_states = len(traj.states)
    if n_states <= window_size:
        return [copy.deepcopy(traj)]
    
    windows = []
    start = 0
    while start < n_states:
        end = min(start + window_size, n_states)
        # Sliced states
        sub_states = [copy.deepcopy(s) for s in traj.states[start:end]]
        if len(sub_states) >= 2:
            sub_states[-1].next_action = None
            sub_traj = Trajectory(objects=traj.objects, states=sub_states)
            windows.append(sub_traj)
        if end >= n_states:
            break
        start += stride
    return windows

def window_trajectories(trajectories, window_size=15, stride=10, max_windows=None):
    """
    Applies sliding windowing across a collection of trajectories.
    Optionally caps total windows to max_windows to keep SAT horizon strictly bounded.
    """
    all_windows = []
    for t in trajectories:
        w_list = window_trajectory(t, window_size=window_size, stride=stride)
        all_windows.extend(w_list)
        if max_windows and len(all_windows) >= max_windows:
            all_windows = all_windows[:max_windows]
            break
    return all_windows

def parse_madagascar_log(log_path):
    """
    Parses Madagascar output log for variable count, clause count, and SAT solving time.
    """
    vars_count = 0
    clauses_count = 0
    if not os.path.exists(log_path):
        return vars_count, clauses_count
    
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    m_vars = re.search(r'(\d+)\s+variables', content)
    if m_vars:
        vars_count = int(m_vars.group(1))
    else:
        m_v2 = re.search(r'variables:\s*(\d+)', content, re.I)
        if m_v2:
            vars_count = int(m_v2.group(1))
            
    m_cls = re.search(r'(\d+)\s+clauses', content)
    if m_cls:
        clauses_count = int(m_cls.group(1))
    else:
        m_c2 = re.search(r'clauses:\s*(\d+)', content, re.I)
        if m_c2:
            clauses_count = int(m_c2.group(1))
            
    return vars_count, clauses_count
