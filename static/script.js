class TodoApp {
    constructor() {
        this.apiBaseUrl = '/api/todos';
        this.init();
    }

    init() {
        this.taskInput = document.getElementById('taskInput');
        this.addButton = document.getElementById('addButton');
        this.tasksContainer = document.getElementById('tasksContainer');
        this.emptyState = document.getElementById('emptyState');
        this.totalTasksSpan = document.getElementById('totalTasks');
        this.completedTasksSpan = document.getElementById('completedTasks');

        this.bindEvents();
        this.loadTodos();
    }

    bindEvents() {
        this.addButton.addEventListener('click', () => this.addTask());
        this.taskInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.addTask();
            }
        });
    }

    async loadTodos() {
        try {
            this.setLoading(true);
            const response = await fetch(this.apiBaseUrl);
            const todos = await response.json();
            this.renderTodos(todos);
            this.updateStats(todos);
        } catch (error) {
            this.showError('Ошибка загрузки задач');
            console.error('Error loading todos:', error);
        } finally {
            this.setLoading(false);
        }
    }

    async addTask() {
        const taskText = this.taskInput.value.trim();

        if (taskText === '') {
            this.showError('Пожалуйста, введите текст задачи');
            return;
        }

        try {
            this.setLoading(true);
            const response = await fetch(this.apiBaseUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: taskText,
                    completed: false
                })
            });

            if (response.ok) {
                this.taskInput.value = '';
                this.loadTodos(); // Перезагружаем список
            } else {
                this.showError('Ошибка при добавлении задачи');
            }
        } catch (error) {
            this.showError('Ошибка при добавлении задачи');
            console.error('Error adding todo:', error);
        } finally {
            this.setLoading(false);
        }
    }

    async updateTodo(id, updates) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updates)
            });

            if (!response.ok) {
                this.showError('Ошибка при обновлении задачи');
            }
        } catch (error) {
            this.showError('Ошибка при обновлении задачи');
            console.error('Error updating todo:', error);
        }
    }

    async deleteTodo(id) {
        if (!confirm('Вы уверены, что хотите удалить эту задачу?')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.loadTodos(); // Перезагружаем список
            } else {
                this.showError('Ошибка при удалении задачи');
            }
        } catch (error) {
            this.showError('Ошибка при удалении задачи');
            console.error('Error deleting todo:', error);
        }
    }

    renderTodos(todos) {
        this.tasksContainer.innerHTML = '';

        if (todos.length === 0) {
            this.emptyState.classList.remove('hidden');
            return;
        }

        this.emptyState.classList.add('hidden');

        todos.forEach(todo => {
            const taskElement = document.createElement('div');
            taskElement.className = `task-item ${todo.completed ? 'completed' : ''}`;
            taskElement.innerHTML = `
                <input type="checkbox" class="task-checkbox" ${todo.completed ? 'checked' : ''}>
                <span class="task-text">${this.escapeHtml(todo.text)}</span>
                <button class="delete-btn">Удалить</button>
            `;

            // Отметка выполнения
            const checkbox = taskElement.querySelector('.task-checkbox');
            checkbox.addEventListener('change', () => {
                this.updateTodo(todo.id, { completed: checkbox.checked });
                taskElement.classList.toggle('completed', checkbox.checked);
                this.loadTodos(); // Обновляем статистику
            });

            // Удаление задачи
            const deleteBtn = taskElement.querySelector('.delete-btn');
            deleteBtn.addEventListener('click', () => {
                this.deleteTodo(todo.id);
            });

            this.tasksContainer.appendChild(taskElement);
        });
    }

    updateStats(todos) {
        const total = todos.length;
        const completed = todos.filter(todo => todo.completed).length;

        this.totalTasksSpan.textContent = total;
        this.completedTasksSpan.textContent = completed;
    }

    setLoading(loading) {
        if (loading) {
            document.body.classList.add('loading');
            this.addButton.disabled = true;
            this.addButton.textContent = 'Добавление...';
        } else {
            document.body.classList.remove('loading');
            this.addButton.disabled = false;
            this.addButton.textContent = 'Добавить';
        }
    }

    showError(message) {
        // Удаляем предыдущие ошибки
        const existingError = document.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }

        const errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        errorElement.textContent = message;

        document.querySelector('.input-section').after(errorElement);

        // Автоматическое скрытие через 5 секунд
        setTimeout(() => {
            errorElement.remove();
        }, 5000);
    }

    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new TodoApp();
});