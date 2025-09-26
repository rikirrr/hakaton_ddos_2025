import argparse
import os
import subprocess
import sys
import tempfile
import shutil

# Поддерживаемые языки
LANG_MAP = {
    "python": ["*.py"],
    "java": ["*.java"],
    "kotlin": ["*.kt", "*.kts"],  # Добавлен .kts для Kotlin script
    "java_script": ["*.js", "*.ts", "*.jsx", "*.tsx"],  # Исправлено с .ks на правильные расширения
    "go": ["*.go"],
    "cpp": ["*.cpp", "*.cc", "*.cxx", "*.c++", "*.hpp", "*.h"]
}

DOCKERS_DIR = "./dockers/"


def show_help_message():
    print("test")


def show_lang_message():
    print("Доступные языки программирования:\n"
          "- python (pure, conda, poetry)\n"
          "- java, kotlin (maven, gradle)\n"
          "- java_script (next.js, node.js)")


def detect_language(project_path: str, max_depth: int = 3) -> str | None:
    """
    Определяет язык программирования, проверяя файлы в поддиректориях.

    Args:
        project_path: Путь к проекту
        max_depth: Максимальная глубина поиска в поддиректориях
    """

    def find_files_with_extensions(path: str, current_depth: int = 0):
        """Рекурсивно ищет файлы с нужными расширениями"""
        found_extensions = set()

        if current_depth > max_depth:
            return found_extensions

        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)

                if os.path.isfile(item_path):
                    # Получаем расширение файла
                    _, ext = os.path.splitext(item)
                    if ext:
                        found_extensions.add(ext)
                elif os.path.isdir(item_path):
                    # Пропускаем системные папки и папки зависимостей
                    skip_dirs = {'.git', '.svn', '__pycache__', 'node_modules',
                                 'target', 'build', '.idea', '.vscode', 'dist'}
                    if item not in skip_dirs:
                        found_extensions.update(
                            find_files_with_extensions(item_path, current_depth + 1)
                        )
        except (PermissionError, OSError):
            # Игнорируем папки без доступа
            pass

        return found_extensions

    # Собираем все расширения файлов в проекте
    all_extensions = find_files_with_extensions(project_path)

    # Проверяем каждый язык
    language_scores = {}
    for lang, patterns in LANG_MAP.items():
        score = 0
        for pattern in patterns:
            ext = "." + pattern.split(".")[-1]  # Получаем расширение из паттерна
            if ext in all_extensions:
                score += 1
        if score > 0:
            language_scores[lang] = score

    # Возвращаем язык с наибольшим количеством совпадений
    if language_scores:
        return max(language_scores.items(), key=lambda x: x[1])[0]

    return None


def detect_language_by_config_files(project_path: str) -> str | None:
    """
    Дополнительное определение языка по конфигурационным файлам
    """
    config_files = {
        "python": ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile", "environment.yml"],
        "java": ["pom.xml"],
        "kotlin": ["build.gradle.kts"],
        "java_script": ["package.json", "yarn.lock", "npm-shrinkwrap.json"],
        "go": ["go.mod", "go.sum"]
    }

    def check_files_recursive(path: str, target_files: set, max_depth: int = 2, current_depth: int = 0):
        if current_depth > max_depth:
            return False

        try:
            for item in os.listdir(path):
                if item in target_files:
                    return True

                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    skip_dirs = {'.git', '.svn', '__pycache__', 'node_modules', 'target', 'build'}
                    if item not in skip_dirs:
                        if check_files_recursive(item_path, target_files, max_depth, current_depth + 1):
                            return True
        except (PermissionError, OSError):
            pass

        return False

    for lang, files in config_files.items():
        if check_files_recursive(project_path, set(files)):
            return lang

    return None


def enhanced_detect_language(project_path: str) -> str | None:
    """
    Улучшенное определение языка: сначала по расширениям файлов, затем по конфигурационным файлам
    """
    # Сначала пробуем определить по расширениям файлов
    lang = detect_language(project_path)

    # Если не получилось, пробуем по конфигурационным файлам
    if not lang:
        lang = detect_language_by_config_files(project_path)

    return lang


def run_docker(lang: str, project_path: str) -> bool:
    """
    Docker сборка и запуск
    """
    dockerfile = os.path.join(DOCKERS_DIR, f"Dockerfile")
    if not os.path.exists(dockerfile):
        print(f"[ОШИБКА] Нет Dockerfile")
        return False

    with tempfile.TemporaryDirectory() as tmpdir:
        build_path = os.path.join(tmpdir, "build")
        shutil.copytree(project_path, build_path)
        shutil.copytree(DOCKERS_DIR, os.path.join(build_path, "dockers"))
        shutil.copy(dockerfile, os.path.join(build_path, "Dockerfile"))

        image_tag = f"project_{lang}"
        # docker build
        result = subprocess.run(
            ["docker", "build", "--build-arg", f"LANG_NAME={lang}", "-t", image_tag, build_path],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        if result.returncode != 0:
            print("[ОШИБКА] Сборка не удалась:")
            print(result.stdout)
            return False

        # docker run
        result = subprocess.run(
            ["docker", "run", "--rm", image_tag],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        if result.returncode == 0:
            print("[УСПЕХ] Программа выполнена:")
            print(result.stdout)
            return True
        else:
            print("[ОШИБКА] Ошибка выполнения:")
            print(result.stdout)
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Утилита для запуска проектов в Docker по GitHub ссылке или директории."
    )
    parser.add_argument("repo_or_path", help="Ссылка на GitHub или путь к проекту")
    parser.add_argument("--lang", help="Язык программирования")
    args = parser.parse_args()

    # Если ссылка на GitHub -> клонируем
    if args.repo_or_path.startswith("http"):
        tmpdir = tempfile.mkdtemp()
        repo_path = os.path.join(tmpdir, "repo")
        result = subprocess.run(["git", "clone", args.repo_or_path, repo_path])
        if result.returncode != 0:
            print("[ОШИБКА] Не удалось клонировать репозиторий.")
            sys.exit(1)
        project_path = repo_path
    else:
        project_path = args.repo_or_path

    # Определяем язык
    lang = args.lang or enhanced_detect_language(project_path)
    if not lang:
        print("[ОШИБКА] Не удалось определить язык проекта.")
        print("Найденные файлы в проекте:")
        # Показываем пользователю какие файлы найдены для отладки
        for root, dirs, files in os.walk(project_path):
            # Пропускаем системные директории
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', 'target', 'build'}]
            level = root.replace(project_path, '').count(os.sep)
            if level < 3:  # Ограничиваем глубину вывода
                indent = ' ' * 2 * level
                print(f"{indent}{os.path.basename(root)}/")
                subindent = ' ' * 2 * (level + 1)
                for file in files[:5]:  # Показываем только первые 5 файлов
                    print(f"{subindent}{file}")
                if len(files) > 5:

                    print(f"{subindent}... и еще {len(files) - 5} файлов")
        sys.exit(1)

    print(f"[ИНФО] Используем язык: {lang}")
    is_lang_correct = input("Всё верно? (1 - да; 2 - нет): ")

    if is_lang_correct == "1":
        success = run_docker(lang, project_path)
        sys.exit(0 if success else 1)
    else:
        print("Возможно данный проект не поддерживается.\n"
              "Попробуйте указать язык программирования самостоятельно через флаг --lang\n"
              "(--help для просмотра поддерживаемых ЯП)")


if __name__ == "__main__":
    main()