def run_with_limits(step_costs, max_steps, max_cost):
    spent = 0.0
    ran = 0
    for cost in step_costs:
        if ran >= max_steps:
            return {"ran": ran, "spent": round(spent, 4), "stopped": "max_steps"}
        if spent + cost > max_cost:
            return {"ran": ran, "spent": round(spent, 4), "stopped": "max_cost"}
        spent += cost
        ran += 1
    return {"ran": ran, "spent": round(spent, 4), "stopped": "done"}
