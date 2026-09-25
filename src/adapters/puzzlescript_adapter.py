"""
PuzzleScript-to-PDDL & Structured Action Trace Adapter Pipeline
Converts PuzzleScript 2D grid rules and engine execution traces into valid STRIPS PDDL fluents and action traces.
"""

import json
import os

class PuzzleScriptAdapter:
    def __init__(self, game_name, grid_width=10, grid_height=10):
        self.game_name = game_name
        self.width = grid_width
        self.height = grid_height
        
    def parse_grid_state_to_fluents(self, grid_matrix):
        """Converts 2D grid matrix into first-order Boolean fluents (predicates)."""
        fluents = []
        for y in range(len(grid_matrix)):
            for x in range(len(grid_matrix[y])):
                cell = grid_matrix[y][x]
                pos = f"pos_{x}_{y}"
                if cell == 'P':
                    fluents.append(f"(at player {pos})")
                elif cell == 'B':
                    fluents.append(f"(at box {pos})")
                elif cell == 'W':
                    fluents.append(f"(is-wall {pos})")
                elif cell == 'T':
                    fluents.append(f"(is-target {pos})")
                elif cell == 'K':
                    fluents.append(f"(has-key player)")
                elif cell == 'D':
                    fluents.append(f"(is-door-locked {pos})")
        return sorted(fluents)

    def generate_pddl_domain_header(self):
        """Generates ground-truth PDDL domain definition for the benchmark."""
        domain_pddl = f"""(define (domain {self.game_name})
  (:requirements :strips :typing)
  (:types position object)
  (:predicates
     (at ?obj - object ?pos - position)
     (is-wall ?pos - position)
     (is-target ?pos - position)
     (has-key ?obj - object)
     (is-door-locked ?pos - position)
     (adjacent ?pos1 - position ?pos2 - position)
  )

  (:action move
     :parameters (?p - object ?from - position ?to - position)
     :precondition (and (at ?p ?from) (adjacent ?from ?to) (not (is-wall ?to)))
     :effect (and (not (at ?p ?from)) (at ?p ?to))
  )

  (:action push-box
     :parameters (?p - object ?b - object ?pfrom - position ?bfrom - position ?bto - position)
     :precondition (and (at ?p ?pfrom) (at ?b ?bfrom) (adjacent ?pfrom ?bfrom) (adjacent ?bfrom ?bto) (not (is-wall ?bto)))
     :effect (and (not (at ?p ?pfrom)) (at ?p ?bfrom) (not (at ?b ?bfrom)) (at ?b ?bto))
  )
)"""
        return domain_pddl

    def convert_trace_to_strips(self, raw_trace):
        """Converts raw PuzzleScript action execution trace into structured STRIPS action step."""
        structured_steps = []
        for idx, step in enumerate(raw_trace):
            action_name = step.get('action')
            state_before = self.parse_grid_state_to_fluents(step.get('state_before'))
            state_after = self.parse_grid_state_to_fluents(step.get('state_after'))
            
            add_list = sorted(list(set(state_after) - set(state_before)))
            del_list = sorted(list(set(state_before) - set(state_after)))
            
            structured_steps.append({
                "step": idx + 1,
                "action": action_name,
                "preconditions_satisfied": state_before,
                "add_effects": add_list,
                "delete_effects": del_list
            })
        return structured_steps
