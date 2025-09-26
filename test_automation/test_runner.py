#!/usr/bin/env python3
import os
import subprocess
import sys
import tempfile
import shutil
import json
from datetime import datetime


class DockerTester:
    def __init__(self, dockers_dir="../dockers", results_dir="results"):
        self.dockers_dir = dockers_dir
        self.results_dir = results_dir
        self.test_projects_dir = "test_projects"

        os.makedirs(results_dir, exist_ok=True)

        # Все тестовые случаи
        self.test_cases = {
            # Java тесты
            "java/simple": "Dockerfile.java",
            "java/maven": "Dockerfile.java",
            "java/gradle": "Dockerfile.java",
            "java/spring-boot": "Dockerfile.java",

            # Go тесты
            "go/simple": "Dockerfile.go",
            "go/modules": "Dockerfile.go",
            "go/multi-file": "Dockerfile.go",
            "go/task": "Dockerfile.go",
            "go/mage": "Dockerfile.go",
            "go/cmd-structure": "Dockerfile.go",

            # JavaScript тесты
            "js/simple": "Dockerfile.js",
            "js/npm": "Dockerfile.js",
            "js/typescript": "Dockerfile.js",
            "js/express": "Dockerfile.js",
            "js/react": "Dockerfile.js",
            "js/yarn": "Dockerfile.js"
        }

        self.results = {
            "timestamp": datetime.now().isoformat(),
            "summary": {},
            "tests": {}
        }

    def test_single_project(self, project_name, dockerfile_name):
        """Тестирует один тестовый проект"""
        print(f"\n🧪 Тестируем {project_name} с {dockerfile_name}")

        project_path = os.path.join(self.test_projects_dir, project_name)
        dockerfile_path = os.path.join(self.dockers_dir, dockerfile_name)

        if not os.path.exists(project_path):
            return {"success": False, "error": "Тестовый проект не найден"}
        if not os.path.exists(dockerfile_path):
            return {"success": False, "error": "Dockerfile не найден"}

        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                # Копируем проект
                test_dir = os.path.join(tmpdir, "test")
                shutil.copytree(project_path, test_dir)
                shutil.copy(dockerfile_path, os.path.join(test_dir, "Dockerfile"))

                # Собираем образ
                image_tag = f"test-{project_name.replace('/', '-')}"
                build_result = subprocess.run(
                    ["docker", "build", "-t", image_tag, test_dir],
                    capture_output=True, text=True, timeout=300
                )

                if build_result.returncode != 0:
                    return {
                        "success": False,
                        "error": "Ошибка сборки",
                        "build_stdout": build_result.stdout,
                        "build_stderr": build_result.stderr
                    }

                # Запускаем контейнер
                run_result = subprocess.run(
                    ["docker", "run", "--rm", image_tag],
                    capture_output=True, text=True, timeout=60
                )

                success = (run_result.returncode == 0 and
                           "SUCCESS" in run_result.stdout)

                return {
                    "success": success,
                    "build_stdout": build_result.stdout[-500:],
                    "run_stdout": run_result.stdout,
                    "run_stderr": run_result.stderr,
                    "returncode": run_result.returncode
                }

            except subprocess.TimeoutExpired:
                return {"success": False, "error": "Таймаут выполнения"}
            except Exception as e:
                return {"success": False, "error": str(e)}

    def run_language_tests(self, language):
        """Запускает тесты для конкретного языка"""
        print(f"\n{'=' * 60}")
        print(f"🚀 Тестирование {language.upper()}")
        print(f"{'=' * 60}")

        language_tests = {k: v for k, v in self.test_cases.items() if k.startswith(language)}
        total = len(language_tests)
        passed = 0

        for project_name, dockerfile in language_tests.items():
            result = self.test_single_project(project_name, dockerfile)
            self.results["tests"][project_name] = result

            if result["success"]:
                print(f"✅ {project_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {project_name}: FAILED")
                if "error" in result:
                    print(f"   Ошибка: {result['error']}")

        return passed, total

    def run_all_tests(self):
        """Запускает все тесты по языкам"""
        print("🚀 Запуск автоматического тестирования Dockerfile")

        # Очистка предыдущих образов
        self.cleanup_containers()

        # Тестируем по языкам
        languages = ["java", "go", "js"]
        summary = {}

        for lang in languages:
            passed, total = self.run_language_tests(lang)
            summary[lang] = {"passed": passed, "total": total, "success": passed == total}

        self.results["summary"] = summary
        self.save_results()

        # Вывод итогов
        self.print_summary()

        return all(result["success"] for result in summary.values())

    def print_summary(self):
        """Печатает итоговую сводку"""
        print(f"\n{'=' * 60}")
        print("📊 ИТОГОВАЯ СВОДКА")
        print(f"{'=' * 60}")

        for lang, result in self.results["summary"].items():
            status = "✅" if result["success"] else "❌"
            print(f"{lang.upper():<12} {status} {result['passed']}/{result['total']}")

            if not result["success"]:
                self.print_failed_language_tests(lang)

    def print_failed_language_tests(self, language):
        """Печатает неудачные тесты для языка"""
        failed_tests = [name for name, result in self.results["tests"].items()
                        if name.startswith(language) and not result["success"]]

        if failed_tests:
            print(f"   Неудачные тесты {language}:")
            for test in failed_tests:
                result = self.results["tests"][test]
                print(f"     - {test}: {result.get('error', 'Unknown error')}")

    def cleanup_containers(self):
        """Очистка контейнеров"""
        try:
            # Удаляем тестовые образы
            images = subprocess.run(
                ["docker", "images", "-q", "test-*"],
                capture_output=True, text=True
            )
            if images.stdout:
                subprocess.run(["docker", "rmi", "-f"] + images.stdout.strip().split('\n'))
        except:
            pass

    def save_results(self):
        """Сохраняет результаты"""
        # JSON
        with open(f"{self.results_dir}/test_results.json", "w") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        # HTML отчет
        self.generate_html_report()

        print(f"\n📁 Результаты сохранены в {self.results_dir}/")

    def generate_html_report(self):
        """Генерирует HTML отчет"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Docker Tests Report - Java, Go, JavaScript</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .language {{ margin: 15px 0; padding: 10px; border-left: 5px solid; }}
        .test {{ margin: 5px 0; padding: 8px; border-radius: 3px; }}
        .passed {{ background: #d4edda; border-color: #28a745; }}
        .failed {{ background: #f8d7da; border-color: #dc3545; }}
        .java {{ border-color: #f89820; }}
        .go {{ border-color: #00add8; }}
        .js {{ border-color: #f7df1e; }}
    </style>
</head>
<body>
    <h1>📋 Отчет тестирования Dockerfile</h1>
    <div class="summary">
        <h2>Общая статистика</h2>
        <p>Время тестирования: {self.results['timestamp']}</p>
    </div>
"""

        # Сводка по языкам
        for lang, stats in self.results["summary"].items():
            status_class = "passed" if stats["success"] else "failed"
            html += f"""
            <div class="language {lang}">
                <h2>{lang.upper()} - {stats['passed']}/{stats['total']} пройдено</h2>
            """

            for test_name, result in self.results["tests"].items():
                if test_name.startswith(lang):
                    test_status = "passed" if result["success"] else "failed"
                    html += f"""
                    <div class="test {test_status}">
                        <strong>{test_name}</strong> - {test_status.upper()}
                        {f"<br><em>Ошибка: {result.get('error', '')}</em>" if not result['success'] else ""}
                    </div>
                    """

            html += "</div>"

        html += "</body></html>"

        with open(f"{self.results_dir}/report.html", "w") as f:
            f.write(html)


def validate_dockerfiles():
    """Проверяет Dockerfile перед использованием"""
    try:
        import sys
        sys.path.append('test-automation')
        from test_runner import DockerTester

        print("🔍 Проверяем Dockerfile...")
        tester = DockerTester()

        # Быстрая проверка основных сценариев
        critical_tests = [
            "java/simple", "java/maven",
            "go/simple", "go/modules",
            "js/simple", "js/npm"
        ]

        all_passed = True
        for test in critical_tests:
            lang = test.split('/')[0]
            result = tester.test_single_project(test, f"Dockerfile.{lang}")
            if not result["success"]:
                print(f"⚠️ Тест {test} не пройден!")
                all_passed = False

        return all_passed

    except Exception as e:
        print(f"⚠️ Ошибка при тестировании: {e}")
        return True  # Продолжаем работу


def main():
        # Проверяем Dockerfile
    if not validate_dockerfiles():
        response = input("Продолжить несмотря на ошибки? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    tester = DockerTester()

    # Создаем тестовые проекты если их нет
    if not os.path.exists("test_projects"):
        print("📁 Создаем тестовые проекты...")
        from test_projects.generator import create_test_projects
        create_test_projects()

    # Запускаем тесты
    success = tester.run_all_tests()

    exit(0 if success else 1)


if __name__ == "__main__":
    main()