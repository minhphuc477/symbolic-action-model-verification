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

    def calculate_theorem1_bounds(self, branching_factor=2, max_depth=5, min_depth_omega=1):
        """
        Calculates theoretical lower and upper GED bounds from Theorem 1:
        Lower Bound = |E_pred| * sum(omega(p*))
        Upper Bound = |E_pred| * sum(omega(p*) * b^(D - depth(p*)))
        """
        if not self.E_pred:
            return 0.0, 0.0
            
        sum_omega = sum(self.calculate_omega(pred) for pred in self.critical_preds)
        lower_bound = len(self.E_pred) * sum_omega
        
        # Upper bound cascades through descendant subtree of depth (D - depth(p*))
        upper_bound = len(self.E_pred) * sum_omega * (branching_factor ** (max_depth - min_depth_omega))
        return lower_bound, upper_bound

    def calculate_tightness_ratio(self, actual_ged, lower_bound):
        """
        Computes tightness ratio T_ratio = actual_ged / lower_bound.
        When T_ratio = 1.0, lower bound is strictly tight (Theorem 3).
        """
        if lower_bound == 0:
            return 1.0
        return actual_ged / lower_bound

    def calculate_accuracy(self):
        r"""
        Calculates passive transition prediction accuracy A_pred on D_test = E_real U (E_pred \ E_real):
        A_pred = |E_real| / (|E_real| + |E_pred \ E_real|)
        """
        phantom_edges = len(self.E_pred - self.E_real)
        d_test_size = len(self.E_real) + phantom_edges
        if d_test_size == 0:
            return 1.0
        return len(self.E_real) / d_test_size

    def compute_all_metrics(self, learned_predicates, branching_factor=2, max_depth=5):
        ged, deleted, added = self.calculate_ged()
        per = self.calculate_per()
        cpr = self.calculate_cpr(learned_predicates)
        acc = self.calculate_accuracy()
        
        omega_dict = {}
        for pred in self.critical_preds:
            omega_dict[pred] = self.calculate_omega(pred)
            
        lower_b, upper_b = self.calculate_theorem1_bounds(branching_factor, max_depth)
        t_ratio = self.calculate_tightness_ratio(ged, lower_b)
            
        return {
            "GED": ged,
            "Deleted_Real_Edges": deleted,
            "Added_Phantom_Edges": added,
            "Accuracy": acc,
            "Accuracy_A_pred_pct": f"{acc * 100:.2f}%",
            "PER_Phantom_Edge_Rate": f"{per * 100:.2f}%",
            "CPR_Critical_Precondition_Recall": f"{cpr * 100:.2f}%",
            "Topological_Cut_Weights_omega": omega_dict,
            "Theorem1_Lower_Bound": lower_b,
            "Theorem1_Upper_Bound": upper_b,
            "Theorem3_Tightness_Ratio": round(t_ratio, 4)
        }

