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
        """
        ground_truth_edges: list of tuples (s, a, s') from G_{T'}
        predicted_edges: list of tuples (s, a, s', violated_predicates) from G_{hat_T}
        critical_predicates: list of bottleneck predicate names
        """
        self.E_real = set((e[0], e[1], e[2]) for e in ground_truth_edges)
        self.E_pred_raw = predicted_edges
        self.E_pred = set((e[0], e[1], e[2]) for e in predicted_edges)
        self.critical_preds = set(critical_predicates)

    def calculate_ged(self):
        """Graph Edit Distance = |E_real \ E_pred| + |E_pred \ E_real|"""
        deleted_edges = len(self.E_real - self.E_pred)
        added_phantom_edges = len(self.E_pred - self.E_real)
        ged = deleted_edges + added_phantom_edges
        return ged, deleted_edges, added_phantom_edges

    def calculate_omega(self, predicate_name):
        """
        Topological Cut-Weight omega(p*) = |{ (s,a,s') in E_pred | predicate_name in violated }| / |E_pred|
        """
        if not self.E_pred_raw:
            return 0.0
        
        violated_count = 0
        for edge in self.E_pred_raw:
            violated_list = edge[3] if len(edge) > 3 else []
            if predicate_name in violated_list:
                violated_count += 1
                
        return violated_count / len(self.E_pred_raw)

    def calculate_per(self):
        """Phantom Edge Rate (PER) = |E_pred \ E_real| / |E_pred|"""
        if not self.E_pred:
            return 0.0
        phantom_edges = self.E_pred - self.E_real
        return len(phantom_edges) / len(self.E_pred)

    def calculate_cpr(self, learned_predicates):
        """
        Critical Precondition Recall (CPR) = |learned & critical| / |critical|
        """
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

# Sample Demonstration & Test Run
if __name__ == "__main__":
    real_edges = [("s0", "act_move", "s1"), ("s1", "act_door", "s2"), ("s2", "act_goal", "s_target")]
    pred_edges = [
        ("s0", "act_move", "s1", []),
        ("s1", "act_door", "s2", ["p_key"]),      # Phantom Edge: violated p_key
        ("s1", "act_shortcut", "s_target", ["p_key"]), # Phantom Edge: violated p_key
        ("s2", "act_goal", "s_target", [])
    ]
    
    calculator = TopologyMetricsCalculator(real_edges, pred_edges, ["p_key"])
    results = calculator.compute_all_metrics(["p_normal"])
    
    print("=== Topology Metrics Calculator Engine Verification ===")
    print(json.dumps(results, indent=2))
    
    with open("f:/Thesis/literature/sample_topology_metrics_report.json", "w") as f:
        json.dump(results, f, indent=2)
