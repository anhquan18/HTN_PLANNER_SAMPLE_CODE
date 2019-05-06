import copy

class WorldState:
    def __init__(self, **kwargs):
        self.state = kwargs
    
    def update_state(self, new_state):
        for name, effect in new_state.items():
            self.state[name] = effect


class CompoundTask:
    def __init__(self, name):
        self.name = name
        self.method_list = None

    def set_method(self, *args):
        self.method_list = args


class Method:
    def __init__(self, name):
        self.name = name
        self.preconditions = {}
        self.subtasks = None

    def set_precondition(self, **kwargs):
        self.preconditions = kwargs

    def set_subtask(self, *args):
        self.subtasks = args


class PrimitiveTask:
    def __init__(self,name):
        self.name = name
        self.preconditions = {}

    def set_precondition(self, **kwargs):
        self.preconditions = kwargs

    def set_effects(self, **kwargs):
        self.effects = kwargs 


class PlanningHistory:
    def reset(self):
        self.f_plan = []
        self.history = []
        self.world_state = None

    def record(self, task, f_plan, world = None):
        self.history.append(task)
        self.f_plan = f_plan
        #self.world_state = copy.deepcopy(world)

    def restore_task(self):
        if self.history:
            return [self.history.pop(-1)]
        return []

    def restore_world_state(self):
        return copy.deepcopy(self.world_state)


class FinalPlan:
    def reset(self):
        self.tasks = []

    def add(self, task):
        self.tasks.append(task)

    def run(self, world):
        for task in self.tasks:
            world.update_state(task.effects)


class Planner:
    def __init__(self, use_history= True):
        self.working_state = None
        self.f_plan = FinalPlan()
        self.his = PlanningHistory()
        self.use_history = use_history

    def check_task_precond(self, task):
        for precondition in task.preconditions.items():
            if precondition not in self.working_state.state.items():
                return False
        return True

    def make_plan(self, tasks_to_process, world):#, DecomHis):
        print ("*"*10+"CREATING A PLAN"+"*"*10)
        self.f_plan.reset()
        self.his.reset()
        self.working_state = copy.deepcopy(world)
        
        while tasks_to_process:
            current_task = tasks_to_process.pop(0)
            if current_task.__class__.__name__ == 'CompoundTask':
                for method in current_task.method_list:
                    if self.check_task_precond(method):
                        self.his.record(current_task, self.f_plan)
                        tasks_to_process = list(method.subtasks) + tasks_to_process
                    elif self.use_history:
                        tasks_to_process = tasks_to_process + self.his.restore_task()
            elif current_task.__class__.__name__ == 'PrimitiveTask':
                if self.check_task_precond(current_task):
                    self.working_state.update_state(current_task.effects)
                    self.f_plan.add(current_task)
                elif self.use_history:
                    tasks_to_process = tasks_to_process + self.his.restore_task()
            else:
                print('WARNING: NO PLAN FOUND')

    def show_plan(self):
        for task in self.f_plan.tasks:
            print(task.name)

    def execute_plan(self, world):
        self.f_plan.run(world)
