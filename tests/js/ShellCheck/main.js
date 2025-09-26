// shellcheck-builder-specific.js
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

class SpecificJavaScriptSHBuilder {
  constructor(scriptPath = './java_script_run.sh') {
    this.scriptPath = scriptPath;
    this.expectedFrameworks = ['next', 'nuxt', '@angular/core', 'vue', 'react'];
  }

  // Основная проверка
  async build() {
    console.log(`🔍 Проверка файла: ${this.scriptPath}\n`);
    
    if (!fs.existsSync(this.scriptPath)) {
      console.error('❌ Файл не найден');
      return false;
    }

    const checks = [
      this.checkFileExists(),
      this.checkShellCheck(),
      this.checkSyntax(),
      this.checkShebang(),
      this.checkSetE(),
      this.checkPackageJsonValidation(),
      this.checkFrameworkDetection(),
      this.checkNpmCommands(),
      this.checkExecUsage(),
      this.checkErrorHandling()
    ];

    const results = await Promise.all(checks);
    const allValid = results.every(result => result.isValid);

    this.printSummary(results);
    return allValid;
  }

  checkFileExists() {
    return {
      name: 'Существование файла',
      isValid: fs.existsSync(this.scriptPath),
      message: fs.existsSync(this.scriptPath) ? 'Файл найден' : 'Файл не существует'
    };
  }

  checkShellCheck() {
    try {
      execSync(`shellcheck "${this.scriptPath}"`, { stdio: 'pipe' });
      return {
        name: 'ShellCheck проверка',
        isValid: true,
        message: 'ShellCheck пройден успешно'
      };
    } catch (error) {
      return {
        name: 'ShellCheck проверка',
        isValid: false,
        message: `ShellCheck ошибки: ${error.stdout.toString().trim()}`
      };
    }
  }

  checkSyntax() {
    try {
      execSync(`bash -n "${this.scriptPath}"`, { stdio: 'pipe' });
      return {
        name: 'Синтаксис bash',
        isValid: true,
        message: 'Синтаксис корректен'
      };
    } catch (error) {
      return {
        name: 'Синтаксис bash',
        isValid: false,
        message: `Синтаксическая ошибка: ${error.message}`
      };
    }
  }

  checkShebang() {
    const content = fs.readFileSync(this.scriptPath, 'utf8');
    const hasShebang = content.startsWith('#!/bin/bash');
    return {
      name: 'Shebang',
      isValid: hasShebang,
      message: hasShebang ? 'Shebang присутствует' : 'Отсутствует #!/bin/bash'
    };
  }

  checkSetE() {
    const content = fs.readFileSync(this.scriptPath, 'utf8');
    const hasSetE = content.includes('set -e');
    return {
      name: 'set -e',
      isValid: hasSetE,
      message: hasSetE ? 'set -e включен' : 'Отсутствует set -e для обработки ошибок'
    };
  }

  checkPackageJsonValidation() {
    const content = fs.readFileSync(this.scriptPath, 'utf8');
    const hasPackageJsonCheck = content.includes('[ ! -f package.json ]') || 
                               content.includes('if [ ! -f package.json ]');
    return {
      name: 'Проверка package.json',
      isValid: hasPackageJsonCheck,
      message: hasPackageJsonCheck ? 'Проверка package.json присутствует' : 'Нет проверки существования package.json'
    };
  }

  checkFrameworkDetection() {
    const content = fs.readFileSync(this.scriptPath, 'utf8');
    const missingFrameworks = this.expectedFrameworks.filter(framework => 
      !content.includes(`"${framework}"`)
    );
    
    return {
      name: 'Обнаружение фреймворков',
      isValid: missingFrameworks.length === 0,
      message: missingFrameworks.length === 0 ? 
        'Все ожидаемые фреймворки присутствуют' : 
        `Отсутствуют проверки для: ${missingFrameworks.join(', ')}`
    };
  }

  checkNpmCommands() {
    const content = fs.readFileSync(this.scriptPath, 'utf8');
    const hasNpmInstall = content.includes('npm install');
    const hasBuildCommands = content.includes('npm run build') || content.includes('yarn build');
    
    return {
      name: 'NPM команды',
      isValid: hasNpmInstall && hasBuildCommands,
      message: hasNpmInstall && hasBuildCommands ? 
        'NPM команды присутствуют' : 
        `Отсутствует: ${!hasNpmInstall ? 'npm install' : ''} ${!hasBuildCommands ? 'build команды' : ''}`
    };
  }

  checkExecUsage() {
    const content = fs.readFileSync(this.scriptPath, 'utf8');
    const execCount = (content.match(/exec /g) || []).length;
    return {
      name: 'Использование exec',
      isValid: execCount > 0,
      message: `Найдено ${execCount} использований exec (правильно для замены процесса)`
    };
  }

  checkErrorHandling() {
    const content = fs.readFileSync(this.scriptPath, 'utf8');
    const hasExit1 = content.includes('exit 1');
    return {
      name: 'Обработка ошибок',
      isValid: hasExit1,
      message: hasExit1 ? 'Есть обработка ошибок (exit 1)' : 'Нет явной обработки ошибок'
    };
  }

  printSummary(results) {
    console.log('\n📊 Результаты проверки:\n');
    
    results.forEach(result => {
      const icon = result.isValid ? '✅' : '❌';
      console.log(`${icon} ${result.name}: ${result.message}`);
    });

    const validCount = results.filter(r => r.isValid).length;
    const totalCount = results.length;
    
    console.log(`\n📈 Итог: ${validCount}/${totalCount} проверок пройдено`);
    
    if (validCount === totalCount) {
      console.log('🎉 Все проверки пройдены успешно!');
    } else {
      console.log('💡 Рекомендации по улучшению скрипта:');
      results.filter(r => !r.isValid).forEach(result => {
        console.log(`   - ${result.name}: ${result.message}`);
      });
    }
  }
}

// Использование
async function main() {
  const builder = new SpecificJavaScriptSHBuilder('./java_script_run.sh');
  const success = await builder.build();
  
  process.exit(success ? 0 : 1);
}

// Запуск если файл выполняется напрямую
if (require.main === module) {
  main().catch(console.error);
}

module.exports = SpecificJavaScriptSHBuilder;