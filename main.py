import argparse
import os
import subprocess
import sys
import tempfile
import shutil


# Поддерживаемые языки
LANG_MAP = {
    "python": "*.py",
    "java": "*.java",
    "kotlin": "*.kt",
    "java_script": ".ks",
    "go": "*.go",
    "cpp": "*.cpp"
}

DOCKERS_DIR = "/dockers"

def show_help_message():
    print("test")

def show_lang_message():
    print("Доступные языки программирования:\n"
          "- python (pure, conda, poetry)\n"
          "- java, kotlin (maven, gradle)\n"
          "- java_script (next.js, node.js)")

def detect_language(project_path: str) -> str | None:
    """
    Определяет язык программирования
    """
    for lang, patterns in LANG_MAP.items():
        for pattern in patterns:
            ext = pattern.split(".")[-1]
            if any(f.endswith(ext) for f in os.listdir(project_path)):
                return lang
    return None


def run_docker(lang: str, project_path: str) -> bool:
    """
    Docker сборка и запуск
    """
    dockerfile = os.path.join(DOCKERS_DIR, f"Dockerfile")
    if not os.path.exists(dockerfile):
        print(f"[ОШИБКА] Нет Dockerfile для языка {lang}")
        return False

    with tempfile.TemporaryDirectory() as tmpdir:
        build_path = os.path.join(tmpdir, "build")
        shutil.copytree(project_path, build_path)
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
    lang = args.lang or detect_language(project_path)
    if not lang:
        print("[ОШИБКА] Не удалось определить язык проекта.")
        sys.exit(1)

    print(f"[ИНФО] Используем язык: {lang}")
    is_lang_correct = input("Всё верно? (1 - да; 2 - нет")

    if is_lang_correct == "1":
        success = run_docker(lang, project_path)
        sys.exit(0 if success else 1)
    else:
        print("Возможно данный проект не поддерживается.\n"
              "Попобуйте указать язык программирования самостоятельно через флаг --lang\n"
              "(--help для просмотра поддерживаемых ЯП)")


if __name__ == "__main__":
    main()
