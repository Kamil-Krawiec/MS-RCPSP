def validate_solution(solution, instance):
    return (validate_assignments(solution, instance) and
            validate_conflicts(solution, instance) and
            validate_skills(solution, instance) and
            validate_precedence_relations(solution, instance))


def validate_assignments(solution, instance):
    # Ensure all tasks are assigned to resources
    assigned_tasks = {task_id for assignments in solution.schedule.values() for _, task_id in assignments}
    all_tasks = set(instance.tasks.keys())
    if assigned_tasks != all_tasks:
        print("TASK ASSIGMENT NOT VALID")
    return assigned_tasks == all_tasks


def validate_conflicts(solution, instance):
    # Ensure no resource is assigned to more than one task at the same time
    for hour, assignments in solution.schedule.items():
        resources = [resource_id for resource_id, _ in assignments]
        if len(resources) != len(set(resources)):
            print("CONFLICTS!")
            return False
    return True


def validate_skills(solution, instance):
    # Ensure resources have the required skills for assigned tasks
    for hour, assignments in solution.schedule.items():
        for resource_id, task_id in assignments:
            resource = instance.resources[resource_id]
            task = instance.tasks[task_id]
            required_skill_index, required_skill_level = task.skills_required
            if not resource.skills[required_skill_index] >= required_skill_level:
                print("SKILLS NOT VALID!")
                return False
    return True


def validate_precedence_relations(solution, instance):
    task_start_times = {}
    for hour, assignments in solution.schedule.items():
        for _, task_id in assignments:
            task_start_times[task_id] = hour

    for task_id, task in instance.tasks.items():
        for predecessor_id in task.predecessor_ids:
            if task_start_times.get(predecessor_id, float('inf')) + instance.tasks[
                predecessor_id].duration >= task_start_times.get(task_id, -1):
                return False
    return True
