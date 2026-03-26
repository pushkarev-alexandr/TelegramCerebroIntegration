from cerebro.core import root_tasks, task_children
from cerebro.aclasses import Task
from pycerebro import database
from config import CEREBRO_USER, CEREBRO_PASSWORD

class Database(database.Database):
    def __init__(self):
        super().__init__()
        self.connection_error_message = None
        if self.connect_from_cerebro_client() != self.CLIENT_CONNECTED:
            try:
                self.connect(CEREBRO_USER, CEREBRO_PASSWORD)
            except Exception as e:
                self.connection_error_message = e

def find_bugs_and_improvements_task() -> Task | None:
    for task in root_tasks():
        if task.name().strip() == 'Pipeline tools':
            for child in task_children(task.id()):
                if child.name().strip() == 'Баги, улучшения':
                    return child

def create_task(task_name: str, definition: str) -> dict[bool, str]:
    task = find_bugs_and_improvements_task()
    if not task:
        return {'success': False, 'error': 'Parent task not found'}

    for child in task_children(task.id()):
        if child.name().strip() == task_name:
            return {'success': False, 'error': 'Task already exists'}

    db = Database()
    if not db.is_connected():
        return {'success': False, 'error': db.connection_error_message or 'Failed to connect to the database'}

    task_id = db.add_task(task.id(), task_name)
    db.add_definition(task_id, definition)
    return {'success': True}


if __name__ == '__main__':
    result = create_task('Test Task', 'Test Definition')
    if not result['success']:
        print(result['error'])
    else:
        print('Task created successfully')
