"""
Topology Metrics Calculation Engine
Calculates:
- Topological Cut-Weight omega(p*)
- Phantom Edge Rate (PER)
- Critical Precondition Recall (CPR)
- Search-Tree Graph Edit Distance (GED)
"""

import json

class TopologyMetricsCalculator:
    def __init__(self, ground_truth_edges, predicted_edges, critical_predicates):
        self.E_real = set((e[0], e[1], e[2]) for e in ground_truth_edges)
        self.E_pred_raw = predicted_edges
        self.E_pred = set((e[0], e[1], e[2]) for e in predicted_edges)
        self.critical_preds = set(critical_predicates)

    def calculate_ged(self):
        deleted_edges = len(self.E_real - self.E_pred)
        added_phantom_edges = len(self.E_pred - self.E_real)
        ged = deleted_edges + added_phantom_edges
        return ged, deleted_edges, added_phantom_edges

    def calculate_omega(self, predicate_name):
        if not self.E_pred_raw:
            return 0.0
        
        violated_count = 0
        for edge in self.E_pred_raw:
            violated_list = edge[3] if len(edge) > 3 else []
            if predicate_name in violated_list:
                violated_count += 1
                
        return violated_count / len(self.E_pred_raw)

    def calculate_per(self):
        if not self.E_pred:
            return 0.0
        phantom_edges = self.E_pred - self.E_real
        return len(phantom_edges) / len(self.E_pred)

    def calculate_cpr(self, learned_predicates):
        if not self.critical_preds:
            return 1.0
        learned_set = set(learned_predicates)
        recalled = self.critical_preds.intersection(learned_set)
        return len(recalled) / len(self.critical_preds)

    def compute_all_metrics(self, learned_predicates):
        ged, deleted, added = self.calculate_ged()
        per = self.calculate_per()
        cpr = self.calculate_cpr(learned_predicates)
        
        omega_dict = {}
        for pred in self.critical_preds:
            omega_dict[pred] = self.calculate_omega(pred)
            
        return {
            "GED": ged,
            "Deleted_Real_Edges": deleted,
            "Added_Phantom_Edges": added,
            "PER_Phantom_Edge_Rate": f"{per * 100:.2f}%",
            "CPR_Critical_Precondition_Recall": f"{cpr * 100:.2f}%",
            "Topological_Cut_Weights_omega": omega_dict
        }
