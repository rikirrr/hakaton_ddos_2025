
# print("hello world! (conda)")

# Билдер для проверки python_run.sh
import os
import subprocess
import sys
import re

class CondaPythonBuilder:
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
    
    def check_package_managers(self):
        """Проверка поддержки менеджеров пакетов"""
        try:
            with open(self.script_path, 'r') as f:
                content = f.read()
            
            missing_managers = []
            for manager in self.supported_managers:
                if manager not in content:
                    missing_managers.append(manager)
            
            return {
                'name': 'Менеджеры пакетов',
                'is_valid': len(missing_managers) == 0,
                'message': 'Все менеджеры присутствуют' if len(missing_managers) == 0 
                          else f'Отсутствуют: {", ".join(missing_managers)}'
            }
        except Exception as e:
            return {
                'name': 'Менеджеры пакетов',
                'is_valid': False,
                'message': f'Ошибка чтения: {e}'
            }
    
    def check_conda_section(self):
        """Проверка секции conda"""
        try:
            with open(self.script_path, 'r') as f:
                content = f.read()
            
            conda_checks = [
                ('environment.yml', 'Проверка environment.yml'),
                ('apt-get update', 'Обновление apt'),
                ('curl miniconda', 'Загрузка Miniconda'),
                ('bash miniconda.sh', 'Установка Miniconda'),
                ('conda env update', 'Обновление conda environment'),
                ('conda activate', 'Активация environment')
            ]
            
            missing = [name for check, name in conda_checks if check not in content]
            
            return {
                'name': 'Секция conda',
                'is_valid': len(missing) == 0,
                'message': 'Все компоненты conda присутствуют' if len(missing) == 0 
                          else f'Отсутствуют: {", ".join(missing)}'
            }
        except Exception as e:
            return {
                'name': 'Секция conda',
                'is_valid': False,
                'message': f'Ошибка чтения: {e}'
            }
    
    def check_conda_safety(self):
        """Проверка безопасности conda установки"""
        try:
            with open(self.script_path, 'r') as f:
                content = f.read()
            
            # Проверка на опасные паттерны
            warnings = []
            
            # Проверка очистки apt lists
            if 'rm -rf /var/lib/apt/lists/*' not in content:
                warnings.append('Нет очистки apt lists')
            
            # Проверка удаления miniconda.sh
            if 'rm miniconda.sh' not in content:
                warnings.append('Нет удаления miniconda.sh')
            
            # Проверка получения имени environment
            if 'ENV_NAME=$(head -1 environment.yml | awk \'{print $2}\')' not in content:
                warnings.append('Нет автоматического определения имени environment')
            
            return {
                'name': 'Безопасность conda',
                'is_valid': len(warnings) == 0,
                'message': 'Безопасность настроена' if len(warnings) == 0 
                          else f'Предупреждения: {", ".join(warnings)}'
            }
        except Exception as e:
            return {
                'name': 'Безопасность conda',
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
    
    def check_path_handling(self):
        """Проверка обработки PATH"""
        try:
            with open(self.script_path, 'r') as f:
                content = f.read()
            
            has_path_export = 'export PATH="/opt/conda/bin:$PATH"' in content
            has_source = 'source /opt/conda/etc/profile.d/conda.sh' in content
            
            return {
                'name': 'Обработка PATH',
                'is_valid': has_path_export and has_source,
                'message': 'PATH настроен правильно' if has_path_export and has_source 
                          else f'Проблемы с PATH: {"нет export" if not has_path_export else ""} {"нет source" if not has_source else ""}'
            }
        except Exception as e:
            return {
                'name': 'Обработка PATH',
                'is_valid': False,
                'message': f'Ошибка чтения: {e}'
            }
    
    def print_summary(self, results):
        """Вывод результатов"""
        print('\n📊 Результаты проверки python_run.sh:\n')
        
        for result in results:
            icon = '✅' if result['is_valid'] else '❌'
            print(f"{icon} {result['name']}: {result['message']}")
        
        valid_count = sum(1 for r in results if r['is_valid'])
        total_count = len(results)
        
        print(f'\n📈 Итог: {valid_count}/{total_count} проверок пройдено')
        
        if valid_count == total_count:
            print('🎉 Все проверки пройдены успешно!')
        else:
            print('\n💡 Рекомендации по улучшению:')
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
            self.check_package_managers(),
            self.check_conda_section(),
            self.check_conda_safety(),
            self.check_exec_usage(),
            self.check_path_handling()
        ]
        
        self.print_summary(checks)
        
        return all(check['is_valid'] for check in checks)

# Функция для запуска проверки
def check_python_run_sh():
    """Запуск проверки python_run.sh"""
    builder = CondaPythonBuilder('./python_run.sh')
    success = builder.build()
    
    if success:
        print('\n🚀 python_run.sh готов к использованию с conda!')
    else:
        print('\n⚠️  Обнаружены проблемы в python_run.sh')
    
    return success

# Запуск проверки если файл выполняется напрямую
if __name__ == "__main__":
    # Сначала выводим основное сообщение
    print("hello world! (conda)")
    print("\n" + "="*50)
    
    # Затем запускаем проверку
    if len(sys.argv) > 1 and sys.argv[1] == '--check':
        success = check_python_run_sh()
        sys.exit(0 if success else 1)
    else:
        # Обычный запуск
        print("Для проверки python_run.sh выполните: python main.py --check")