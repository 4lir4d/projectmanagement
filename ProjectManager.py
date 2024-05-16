# project management software wasy to use
import redis

class Task:
    def __init__(self, title, description, completed, tags):
        self.title = title
        self.description = description
        self.completed = completed
        self.tags = tags

    def __str__(self):
        #status = "Done" if self.completed else "Pending"
        if (self.completed == "False"):
            status = "Pending"
            status_color = "\033[91m" # RED
        else:
            status = "Done"
            status_color = "\033[92m" #Green
        #print(status)
        reset_color = "\033[0m"
        blue_color = "\033[94m" #Green
        return f"{self.title} - {self.description} [{status_color}{status}{reset_color}] Tags: {blue_color}{', '.join(self.tags)}{reset_color}"
    

class ProjectManager:
    def __init__(self, db_index=0):
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=db_index)
        self.tasks_key = 'tasks'

    def add_task(self, title, description, completed, tags):
        task = Task(title, description, completed, tags)
        task_data = f"{task.title}|{task.description}|{task.completed}|{','.join(task.tags)}"
        self.redis_client.rpush(self.tasks_key, task_data)
        print("Task added successfully.")

    def list_tasks(self):
        tasks_data = self.redis_client.lrange(self.tasks_key, 0, -1)
        if not tasks_data:
            print("No tasks.")
        else:
            for idx, task_data in enumerate(tasks_data, start=1):
                task_info = task_data.decode('utf-8').split('|')
                title, description, completed, tags = task_info
                completed_status = "Done" if completed == "True" else "Pending"
                #print(completed)
                tags_list = tags.split(',')
                task = Task(title, description, completed, tags_list)
                print(f"{idx}. {task}")

    def list_tasks_by_tag(self, tag):
        tasks_data = self.redis_client.lrange(self.tasks_key, 0, -1)
        found_tasks = []
        if not tasks_data:
            print("No tasks.")
        else:
            for task_data in tasks_data:
                task_info = task_data.decode('utf-8').split('|')
                title, description, completed, tags = task_info
                tags_list = tags.split(',')
                if tag in tags_list:
                    task = Task(title, description, completed, tags_list)
                    found_tasks.append(task)
            if found_tasks:
                print(f"Tasks with tag '{tag}':")
                for idx, task in enumerate(found_tasks, start=1):
                    print(f"{idx}. {task}")
            else:
                print(f"No tasks found with tag '{tag}'.")

    def menu(self):
        while True:
            print("\n===== Project Manager =====")
            print("1. Add Task")
            print("2. List Tasks")
            print("3. List Tasks by Tag")
            print("4. Mark Task as Complete/Pending")
            print("5. Delete Task")
            print("6. Exit")

            choice = input("Enter your choice: ")

            if choice == '1':
                title = input("Enter task title: ")
                description = input("Enter task description: ")
                tags_input = input("Enter tags (comma-separated): ")
                tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
                completed = False
                self.add_task(title, description, completed, tags)
            elif choice == '2':
                self.list_tasks()
            elif choice == '3':
                tag = input("Enter tag to search: ")
                self.list_tasks_by_tag(tag)
            elif choice == '4':
                task_index = int(input("Enter task index to mark as complete: "))
                self.mark_task_complete(task_index)
            elif choice == '5':
                task_index = int(input("Enter task index to delete: "))
                self.delete_task(task_index)
            elif choice == '6':
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")

    def mark_task_complete(self, task_index):
        tasks_data = self.redis_client.lrange(self.tasks_key, 0, -1)
        
        if 1 <= task_index <= len(tasks_data):
            # Retrieve task data for the specified task_index
            task_data = tasks_data[task_index - 1].decode('utf-8')
            task_info = task_data.split('|')
            
            # Print current task data before update
            # print("Task Data Before Update:")
            # print(task_info)
            
            # Extract the current completion status (convert to bool)
            current_status = task_info[2] == "True"  # Convert "True" or "False" to bool
            
            # Toggle the completion status
            new_status = not current_status  # Toggle the boolean value
            
            # Update the completion status in task_info
            task_info[2] = "True" if new_status else "False"  # Convert bool back to "True" or "False"
            
                
            # Join task info back into a string
            updated_task_data = '|'.join(task_info)
            
            # Print updated task data
            # print("Updated Task Data:")
            # print(updated_task_data)
            
            # Update the task data in Redis at the specified index
            self.redis_client.lset(self.tasks_key, task_index - 1, updated_task_data)
            
            # Print success message
            print("Task marked as complete.")
        else:
            # Invalid task index provided
            print("Invalid task index.")



    def delete_task(self, task_index):
        tasks_data = self.redis_client.lrange(self.tasks_key, 0, -1)
        if 1 <= task_index <= len(tasks_data):
            self.redis_client.lpop(self.tasks_key)
            print("Task deleted.")
        else:
            print("Invalid task index.")

if __name__ == "__main__":
    manager = ProjectManager()
    manager.menu()
