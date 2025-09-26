# print("hello world! (poetry)")


# main.py
print("hello world! (poetry)")

# Билдер для проверки python_run.sh с фокусом на Poetry
import os
import subprocess
import sys
import re

class PoetryPythonBuilder:
    def __init__(self, script_path='./python_run.sh'):
        self.script_path = script_path
        self.supported_managers = ['requirements.txt', 'pyproject.toml', 'environment.yml']
    
    def check_file_exists(self):
        """Проверка существования файла"""
        exists = os.path.exists(self.script_path)
        return {
            'name': 'Существование файла',
            'is_valid': exists,
            'message': 'Файл найден' if exists else 'Файл не существует'
        }
    
    def check_syntax(self):
        """Проверка синтаксиса bash"""
        try:
            subprocess.run(['bash', '-n', self.script_path], 
                         check=True, capture_output=True)
            return {
                'name': 'Синтаксис bash',
                'is_valid': True,
                'message': 'Синтаксис корректен'
            }
        except subprocess.CalledProcessError as e:
            return {
                'name': 'Синтаксис bash',
                'is_valid': False,
                'message': f'Синтаксическая ошибка: {e.stderr.decode().strip()}'
            }
    
    def check_shebang(self):
        """Проверка shebang"""
        try:
            with open(self.script_path, 'r') as f:
                first_line = f.readline().strip()
            has_shebang = first_line == '#!/bin/bash'
            return {
                'name': 'Shebang',
                'is_valid': has_shebang,
                'message': 'Shebang присутствует' if has_shebang else 'Отсутствует #!/bin/bash'
            }
        except Exception as e:
            return {
                'name': 'Shebang',
                'is_valid': False,
                'message': f'Ошибка чтения: {e}'
            }
    
    def check_set_e(self):
        """Проверка set -e"""
        try:
            with open(self.script_path, 'r') as f:
                content = f.read()
            has_set_e = 'set -e' in content
            return {
                'name': 'set -e',
                'is_valid': has_set_e,
                'message': 'set -e включен' if has_set_e else 'Отсутствует set -e'
            }
        except Exception as e:
            return {
                'name': 'set -e',
                'is_valid': False,
                'message': f'Ошибка чтения: {e}'
            }
    
    def check_poetry_section(self):
        """Проверка секции Poetry"""
        try:
            with open(self.script_path, 'r') as f:
                content = f.read()
            
            poetry_checks = [
                ('pyproject.toml', 'Проверка pyproject.toml'),
                ('pip install poetry', 'Установка Poetry'),
                ('poetry install --no-root', 'Установка зависимостей Poetry'),
                ('echo "Установка через poetry"', 'Сообщение о Poetry')
            ]
            
            missing = [name for check, name in poetry_checks if check not in content]
            
            return {
                'name': 'Секция Poetry',
                'is_valid': len(missing) == 0,
                'message': 'Все компоненты Poetry присутствуют' if len(missing) == 0 
                          else f'Отсутствуют: {", ".join(missing)}'
            }
        except Exception as e:
            return {
                'name': 'Секция Poetry',
                'is_valid': False,
                'message': f'Ошибка чтения: {e}'
            }
    
    def check_poetry_installation(self):
        """Проверка правильности установки Poetry"""
        try:
            with open(self.script_path, 'r') as f:
                content = f.read()
            
            # Проверка правильной последовательности установки Poetry
            lines = content.split('\n')
            poetry_section = False
            issues = []
            
            for i, line in enumerate(lines):
                if 'Установка через poetry' in line:
                    poetry_section = True
                elif poetry_section and 'pip install poetry' in line:
                    # Проверяем что после установки poetry идет poetry install
                    next_lines = lines[i+1:i+3]
                    if not any('poetry install' in nl for nl in next_lines):
                        issues.append('После установки Poetry нет poetry install')
                    break
            
            return {
                'name': 'Установка Poetry',
                'is_valid': len(issues) == 0,
                'message': 'Poetry установлен правильно' if len(issues) == 0 
                          else f'Проблемы: {", ".join(issues)}'
            }
        except Exception as e:
            return {
                'name': 'Установка Poetry',
                'is_valid': False,
                'message': f'Ошибка чтения: {e}'
            }
    
    def check_poetry_flags(self):
        """Проверка флагов Poetry"""
        try:
            with open(self.script_path, 'r') as f:
                content = f.read()
            
            # Проверка использования --no-root (рекомендуется для Docker)
            has_no_root = '--no-root' in content
            
            return {
                'name': 'Флаги Poetry',
                'is_valid': has_no_root,
                'message': 'Используется --no-root (правильно для Docker)' if has_no_root 
                          else 'Отсутствует --no-root флаг'
            }
        except Exception as e:
            return {
                'name': 'Флаги Poetry',
                'is_valid': False,
                'message': f'Ошибка чтения: {e}'
            }
    
    def check_priority_order(self):
        """Проверка порядка приоритета менеджеров"""
        try:
            with open(self.script_path, 'r') as f:
                content = f.read()
            
            # Проверяем порядок условий
            lines = content.split('\n')
            managers_order = []
            
            for line in lines:
                if 'requirements.txt' in line and 'if' in line:
                    managers_order.append('requirements.txt')
                elif 'pyproject.toml' in line and 'if' in line:
                    managers_order.append('pyproject.toml')
                elif 'environment.yml' in line and 'if' in line:
                    managers_order.append('environment.yml')
            
            # Правильный порядок: requirements.txt -> pyproject.toml -> environment.yml
            correct_order = ['requirements.txt', 'pyproject.toml', 'environment.yml']
            is_correct_order = managers_order == correct_order
            
            return {
                'name': 'Порядок менеджеров',
                'is_valid': is_correct_order,
                'message': f'Порядок правильный: {" -> ".join(managers_order)}' if is_correct_order 
                          else f'Неправильный порядок: {" -> ".join(managers_order)} (должен быть: {" -> ".join(correct_order)})'
            }
        except Exception as e:
            return {
                'name': 'Порядок менеджеров',
                'is_valid': False,
                'message': f'Ошибка чтения: {e}'
            }
    
    def check_exec_usage(self):
        """Проверка использования exec"""
        try:
            with open(self.script_path, 'r') as f:
                content = f.read()
            
            has_exec = 'exec python main.py' in content
            return {
                'name': 'Использование exec',
                'is_valid': has_exec,
                'message': 'exec используется правильно' if has_exec else 'Нет exec для запуска Python'
            }
        except Exception as e:
            return {
                'name': 'Использование exec',
                'is_valid': False,
                'message': f'Ошибка чтения: {e}'
            }
    
    def check_virtualenv_handling(self):
        """Проверка обработки virtualenv для Poetry"""
        try:
            with open(self.script_path, 'r') as f:
                content = f.read()
            
            # Poetry автоматически создает virtualenv, проверяем что нет конфликтующих команд
            conflicting_commands = [
                'virtualenv',
                'python -m venv',
                'source venv',
                'conda activate'  # Может конфликтовать с Poetry
            ]
            
            conflicts = [cmd for cmd in conflicting_commands if cmd in content and 'conda activate "$ENV_NAME"' not in cmd]
            
            return {
                'name': 'Обработка virtualenv',
                'is_valid': len(conflicts) == 0,
                'message': 'Virtualenv обрабатывается правильно' if len(conflicts) == 0 
                          else f'Возможные конфликты: {", ".join(conflicts)}'
            }
        except Exception as e:
            return {
                'name': 'Обработка virtualenv',
                'is_valid': False,
                'message': f'Ошибка чтения: {e}'
            }
    
    def check_poetry_config_recommendations(self):
        """Рекомендации по конфигурации Poetry"""
        try:
            with open(self.script_path, 'r') as f:
                content = f.read()
            
            recommendations = []
            
            # Проверка рекомендуемых настроек для Docker
            if 'poetry config virtualenvs.create false' not in content:
                recommendations.append('Рассмотрите poetry config virtualenvs.create false для Docker')
            
            if 'poetry config virtualenvs.in-project true' not in content:
                recommendations.append('Рассмотрите poetry config virtualenvs.in-project true')
            
            return {
                'name': 'Рекомендации Poetry',
                'is_valid': True,  # Всегда валидно, это рекомендации
                'message': 'OK' if len(recommendations) == 0 else f'Рекомендации: {"; ".join(recommendations)}'
            }
        except Exception as e:
            return {
                'name': 'Рекомендации Poetry',
                'is_valid': True,  # Рекомендации не влияют на валидность
                'message': f'Ошибка чтения: {e}'
            }
    
    def print_summary(self, results):
        """Вывод результатов"""
        print('\n📊 Результаты проверки python_run.sh (Poetry focus):\n')
        
        for result in results:
            icon = '✅' if result['is_valid'] else '❌'
            print(f"{icon} {result['name']}: {result['message']}")
        
        # Считаем только основные проверки (исключая рекомендации)
        main_checks = [r for r in results if 'Рекомендации' not in r['name']]
        valid_count = sum(1 for r in main_checks if r['is_valid'])
        total_count = len(main_checks)
        
        print(f'\n📈 Итог: {valid_count}/{total_count} проверок пройдено')
        
        if valid_count == total_count:
            print('🎉 Все основные проверки пройдены успешно!')
        else:
            print('\n💡 Рекомендации по улучшению:')
            for result in main_checks:
                if not result['is_valid']:
                    print(f'   - {result["name"]}: {result["message"]}')
        
        # Отдельно выводим рекомендации
        recommendation_results = [r for r in results if 'Рекомендации' in r['name']]
        for rec in recommendation_results:
            if 'OK' not in rec['message']:
                print(f'💡 {rec["name"]}: {rec["message"]}')
    
    def build(self):
        """Основная функция проверки"""
        print(f'🔍 Проверка файла: {self.script_path}\n')
        
        if not os.path.exists(self.script_path):
            print('❌ Файл не найден')
            return False
        
        checks = [
            self.check_file_exists(),
            self.check_syntax(),
            self.check_shebang(),
            self.check_set_e(),
            self.check_poetry_section(),
            self.check_poetry_installation(),
            self.check_poetry_flags(),
            self.check_priority_order(),
            self.check_exec_usage(),
            self.check_virtualenv_handling(),
            self.check_poetry_config_recommendations()
        ]
        
        self.print_summary(checks)
        
        # Игнорируем рекомендации при определении успешности
        main_checks = [r for r in checks if 'Рекомендации' not in r['name']]
        return all(check['is_valid'] for check in main_checks)

# Функция для запуска проверки
def check_python_run_sh_poetry():
    """Запуск проверки python_run.sh с фокусом на Poetry"""
    builder = PoetryPythonBuilder('./python_run.sh')
    success = builder.build()
    
    if success:
        print('\n🚀 python_run.sh готов к использованию с Poetry!')
        print('💡 Для лучшей интеграции с Docker рассмотрите:')
        print('   - poetry config virtualenvs.create false')
        print('   - poetry config virtualenvs.in-project true')
    else:
        print('\n⚠️  Обнаружены проблемы в python_run.sh')
    
    return success

# Запуск проверки если файл выполняется напрямую
if __name__ == "__main__":
    # Сначала выводим основное сообщение
    print("hello world! (poetry)")
    print("\n" + "="*50)
    
    # Затем запускаем проверку
    if len(sys.argv) > 1 and sys.argv[1] == '--check-poetry':
        success = check_python_run_sh_poetry()
        sys.exit(0 if success else 1)
    elif len(sys.argv) > 1 and sys.argv[1] == '--check':
        # Совместимость с предыдущей версией
        from main import CondaPythonBuilder
        builder = CondaPythonBuilder('./python_run.sh')
        success = builder.build()
        sys.exit(0 if success else 1)
    else:
        # Обычный запуск
        print("Для проверки python_run.sh выполните:")
        print("  python main.py --check-poetry  (фокус на Poetry)")
        print("  python main.py --check         (общая проверка)")