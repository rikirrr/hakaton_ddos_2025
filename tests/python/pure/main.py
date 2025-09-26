# main.py
# print("hello world! (pure)")

# Билдер для проверки python_run.sh с фокусом на чистый Python (без зависимостей)
import os
import subprocess
import sys
import re
import tempfile  # Добавляем импорт tempfile

class PurePythonBuilder:
    def __init__(self, script_path='./python_run.sh'):
        self.script_path = script_path
    
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
        """Проверка set -e для обработки ошибок"""
        try:
            with open(self.script_path, 'r') as f:
                content = f.read()
            has_set_e = 'set -e' in content
            return {
                'name': 'Обработка ошибок',
                'is_valid': has_set_e,
                'message': 'set -e включен (выход при ошибках)' if has_set_e else 'Отсутствует set -e'
            }
        except Exception as e:
            return {
                'name': 'Обработка ошибок',
                'is_valid': False,
                'message': f'Ошибка чтения: {e}'
            }
    
    def check_fallback_behavior(self):
        """Проверка поведения по умолчанию (без зависимостей)"""
        try:
            with open(self.script_path, 'r') as f:
                content = f.read()
            
            # Проверяем, что скрипт выполнит exec python main.py даже без файлов зависимостей
            lines = content.split('\n')
            in_condition = False
            condition_depth = 0
            exec_found = False
            
            for line in lines:
                # Отслеживаем вложенность условий
                if line.strip().startswith('if [') or line.strip().startswith('elif ['):
                    if not in_condition:
                        in_condition = True
                    condition_depth += 1
                elif line.strip() == 'fi':
                    condition_depth -= 1
                    if condition_depth == 0:
                        in_condition = False
                
                # Проверяем exec вне условий
                if 'exec python main.py' in line and not in_condition and condition_depth == 0:
                    exec_found = True
                    break
            
            return {
                'name': 'Fallback поведение',
                'is_valid': exec_found,
                'message': 'Python запустится даже без файлов зависимостей' if exec_found 
                          else 'exec находится внутри условий, может не выполниться'
            }
        except Exception as e:
            return {
                'name': 'Fallback поведение',
                'is_valid': False,
                'message': f'Ошибка чтения: {e}'
            }
    
    def check_no_dependencies_scenario(self):
        """Проверка сценария без файлов зависимостей"""
        try:
            with open(self.script_path, 'r') as f:
                content = f.read()
            
            # Упрощенная проверка без временной директории
            # Анализируем логику скрипта статически
            lines = content.split('\n')
            has_conditions = False
            has_final_exec = False
            
            for i, line in enumerate(lines):
                if line.strip().startswith('if [') or line.strip().startswith('elif ['):
                    has_conditions = True
                if 'exec python main.py' in line:
                    # Проверяем, что это последний exec после всех условий
                    remaining_lines = lines[i+1:]
                    if not any('exec python' in l for l in remaining_lines):
                        has_final_exec = True
            
            # Если есть условия, но exec находится в правильном месте - OK
            if has_conditions and has_final_exec:
                return {
                    'name': 'Сценарий без зависимостей',
                    'is_valid': True,
                    'message': 'Скрипт корректно обрабатывает случай без зависимостей'
                }
            else:
                return {
                    'name': 'Сценарий без зависимостей',
                    'is_valid': False,
                    'message': 'Проблемы с логикой выполнения без зависимостей'
                }
                    
        except Exception as e:
            return {
                'name': 'Сценарий без зависимостей',
                'is_valid': False,
                'message': f'Ошибка анализа: {e}'
            }
    
    def check_exec_placement(self):
        """Проверка размещения exec команды"""
        try:
            with open(self.script_path, 'r') as f:
                content = f.read()
            
            # Проверяем, что exec находится в правильном месте (после всех условий)
            lines = content.split('\n')
            exec_line = -1
            last_fi_line = -1
            
            for i, line in enumerate(lines):
                if 'exec python main.py' in line:
                    exec_line = i
                if line.strip() == 'fi':
                    last_fi_line = i
            
            is_after_conditions = exec_line > last_fi_line and last_fi_line != -1
            
            return {
                'name': 'Размещение exec',
                'is_valid': is_after_conditions,
                'message': 'exec размещен после всех условий' if is_after_conditions 
                          else 'exec должен быть после всех условий (после fi)'
            }
        except Exception as e:
            return {
                'name': 'Размещение exec',
                'is_valid': False,
                'message': f'Ошибка чтения: {e}'
            }
    
    def check_minimal_requirements(self):
        """Проверка минимальных требований для чистого Python"""
        try:
            with open(self.script_path, 'r') as f:
                content = f.read()
            
            issues = []
            
            # Проверяем наличие основных компонентов
            if 'exec python main.py' not in content:
                issues.append('Нет команды запуска Python')
            
            # Упрощенная проверка баланса if/fi
            if_count = content.count('if [')
            fi_count = content.count('fi')
            if if_count != fi_count:
                issues.append(f'Несбалансированные if/fi: {if_count} if, {fi_count} fi')
            
            # Проверяем, что все файлы зависимостей проверяются как опциональные
            mandatory_files = ['requirements.txt', 'pyproject.toml', 'environment.yml']
            for file in mandatory_files:
                if f'[ -f {file} ]' not in content:
                    issues.append(f'Нет проверки для {file}')
            
            return {
                'name': 'Минимальные требования',
                'is_valid': len(issues) == 0,
                'message': 'Минимальные требования выполнены' if len(issues) == 0 
                          else f'Проблемы: {", ".join(issues)}'
            }
        except Exception as e:
            return {
                'name': 'Минимальные требования',
                'is_valid': False,
                'message': f'Ошибка чтения: {e}'
            }
    
    def check_simplicity(self):
        """Проверка простоты и читаемости скрипта"""
        try:
            with open(self.script_path, 'r') as f:
                content = f.read()
            
            lines = content.split('\n')
            non_empty_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
            
            # Проверяем длину скрипта
            line_count = len(non_empty_lines)
            is_concise = line_count <= 30  # Разумный предел для простого скрипта
            
            # Проверяем сложность условий
            condition_count = content.count('if [') + content.count('elif [')
            is_simple = condition_count <= 5  # Не слишком много ветвлений
            
            return {
                'name': 'Простота скрипта',
                'is_valid': is_concise and is_simple,
                'message': f'Скрипт простой ({line_count} строк, {condition_count} условий)' 
                          if is_concise and is_simple 
                          else f'Скрипт может быть сложным: {line_count} строк, {condition_count} условий'
            }
        except Exception as e:
            return {
                'name': 'Простота скрипта',
                'is_valid': True,  # Не критично
                'message': f'Ошибка чтения: {e}'
            }
    
    def check_portability(self):
        """Проверка переносимости скрипта"""
        try:
            with open(self.script_path, 'r') as f:
                content = f.read()
            
            # Проверяем использование переносимых конструкций
            portability_issues = []
            
            # Shebang использует /bin/bash (стандартно)
            if not content.startswith('#!/bin/bash'):
                portability_issues.append('Нестандартный shebang')
            
            return {
                'name': 'Переносимость',
                'is_valid': len(portability_issues) == 0,
                'message': 'Скрипт переносимый' if len(portability_issues) == 0 
                          else f'Проблемы переносимости: {", ".join(portability_issues)}'
            }
        except Exception as e:
            return {
                'name': 'Переносимость',
                'is_valid': False,
                'message': f'Ошибка чтения: {e}'
            }
    
    def check_conditional_logic(self):
        """Проверка условной логики"""
        try:
            with open(self.script_path, 'r') as f:
                content = f.read()
            
            # Проверяем корректность условных конструкций
            lines = content.split('\n')
            issues = []
            
            for i, line in enumerate(lines):
                line = line.strip()
                # Проверяем синтаксис условий
                if line.startswith('if [') and not line.endswith(']'):
                    issues.append(f'Строка {i+1}: незакрытая квадратная скобка в условии')
                elif line.startswith('elif [') and not line.endswith(']'):
                    issues.append(f'Строка {i+1}: незакрытая квадратная скобка в elif')
            
            return {
                'name': 'Условная логика',
                'is_valid': len(issues) == 0,
                'message': 'Условные конструкции корректны' if len(issues) == 0 
                          else f'Проблемы: {"; ".join(issues)}'
            }
        except Exception as e:
            return {
                'name': 'Условная логика',
                'is_valid': False,
                'message': f'Ошибка чтения: {e}'
            }
    
    def print_summary(self, results):
        """Вывод результатов"""
        print('\n📊 Результаты проверки python_run.sh (Pure Python focus):\n')
        
        for result in results:
            icon = '✅' if result['is_valid'] else '❌'
            print(f"{icon} {result['name']}: {result['message']}")
        
        valid_count = sum(1 for r in results if r['is_valid'])
        total_count = len(results)
        
        print(f'\n📈 Итог: {valid_count}/{total_count} проверок пройдено')
        
        if valid_count == total_count:
            print('🎉 Скрипт идеален для чистого Python!')
            print('💡 Скрипт будет работать даже без файлов зависимостей')
        else:
            print('\n💡 Рекомендации для чистого Python:')
            for result in results:
                if not result['is_valid']:
                    print(f'   - {result["name"]}: {result["message"]}')
    
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
            self.check_fallback_behavior(),
            self.check_no_dependencies_scenario(),
            self.check_exec_placement(),
            self.check_minimal_requirements(),
            self.check_conditional_logic(),
            self.check_simplicity(),
            self.check_portability()
        ]
        
        self.print_summary(checks)
        
        return all(check['is_valid'] for check in checks)

# Функция для запуска проверки
def check_python_run_sh_pure():
    """Запуск проверки python_run.sh для чистого Python"""
    builder = PurePythonBuilder('./python_run.sh')
    success = builder.build()
    
    if success:
        print('\n🚀 python_run.sh готов для чистого Python!')
        print('💡 Скрипт будет работать в любой среде с Python и bash')
    else:
        print('\n⚠️  Обнаружены проблемы для чистого Python сценария')
    
    return success

# Запуск проверки если файл выполняется напрямую
if __name__ == "__main__":
    # Сначала выводим основное сообщение
    print("hello world! (pure)")
    print("\n" + "="*50)
    
    # Затем запускаем проверку
    if len(sys.argv) > 1 and sys.argv[1] == '--check-pure':
        success = check_python_run_sh_pure()
        sys.exit(0 if success else 1)
    elif len(sys.argv) > 1 and sys.argv[1] == '--check-poetry':
        # Импортируем и запускаем Poetry проверку
        try:
            from main import check_python_run_sh_poetry
            success = check_python_run_sh_poetry()
            sys.exit(0 if success else 1)
        except ImportError:
            print("❌ Poetry проверка не доступна")
            sys.exit(1)
    elif len(sys.argv) > 1 and sys.argv[1] == '--check':
        # Импортируем и запускаем общую проверку
        try:
            from main import CondaPythonBuilder
            builder = CondaPythonBuilder('./python_run.sh')
            success = builder.build()
            sys.exit(0 if success else 1)
        except ImportError:
            print("❌ Общая проверка не доступна")
            sys.exit(1)
    else:
        # Обычный запуск
        print("Для проверки python_run.sh выполните:")
        print("  python main.py --check-pure     (фокус на чистый Python)")
        print("  python main.py --check-poetry   (фокус на Poetry)")
        print("  python main.py --check          (общая проверка)")