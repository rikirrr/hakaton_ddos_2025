#!/usr/bin/env python3
import os
import shutil


def create_java_projects(base_dir):
    """Создает Java тестовые проекты"""
    java_dir = f"{base_dir}/java"
    os.makedirs(java_dir, exist_ok=True)

    # 1. Простой Java проект
    simple_java = f"{java_dir}/simple"
    os.makedirs(simple_java)
    with open(f"{simple_java}/Main.java", "w") as f:
        f.write('''public class Main {
    public static void main(String[] args) {
        System.out.println("JAVA SIMPLE: SUCCESS!");
    }
}''')

    # 2. Maven проект
    maven_java = f"{java_dir}/maven"
    os.makedirs(f"{maven_java}/src/main/java/com/test")
    with open(f"{maven_java}/pom.xml", "w") as f:
        f.write('''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.test</groupId>
    <artifactId>maven-app</artifactId>
    <version>1.0.0</version>
    <properties>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>
    <dependencies>
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <version>4.13.2</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>org.codehaus.mojo</groupId>
                <artifactId>exec-maven-plugin</artifactId>
                <version>3.1.0</version>
                <configuration>
                    <mainClass>com.test.Main</mainClass>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>''')
    with open(f"{maven_java}/src/main/java/com/test/Main.java", "w") as f:
        f.write('''package com.test;
public class Main {
    public static void main(String[] args) {
        System.out.println("JAVA MAVEN: SUCCESS!");
    }
}''')

    # 3. Gradle проект
    gradle_java = f"{java_dir}/gradle"
    os.makedirs(f"{gradle_java}/src/main/java/com/test")
    with open(f"{gradle_java}/build.gradle", "w") as f:
        f.write('''plugins {
    id 'java'
    id 'application'
}

group = 'com.test'
version = '1.0.0'
sourceCompatibility = '17'

application {
    mainClass = 'com.test.Main'
}

repositories {
    mavenCentral()
}

dependencies {
    testImplementation 'junit:junit:4.13.2'
}

jar {
    manifest {
        attributes 'Main-Class': 'com.test.Main'
    }
}''')
    with open(f"{gradle_java}/src/main/java/com/test/Main.java", "w") as f:
        f.write('''package com.test;
public class Main {
    public static void main(String[] args) {
        System.out.println("JAVA GRADLE: SUCCESS!");
    }
}''')

    # 4. Spring Boot проект (упрощенный)
    spring_java = f"{java_dir}/spring-boot"
    os.makedirs(f"{spring_java}/src/main/java/com/test")
    with open(f"{spring_java}/pom.xml", "w") as f:
        f.write('''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.1.0</version>
    </parent>
    <groupId>com.test</groupId>
    <artifactId>spring-app</artifactId>
    <version>1.0.0</version>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter</artifactId>
        </dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>''')
    with open(f"{spring_java}/src/main/java/com/test/Application.java", "w") as f:
        f.write('''package com.test;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application implements CommandLineRunner {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }

    @Override
    public void run(String... args) {
        System.out.println("JAVA SPRING BOOT: SUCCESS!");
        System.exit(0);
    }
}''')


def create_go_projects(base_dir):
    """Создает Go тестовые проекты"""
    go_dir = f"{base_dir}/go"
    os.makedirs(go_dir, exist_ok=True)

    # 1. Простой Go проект
    simple_go = f"{go_dir}/simple"
    os.makedirs(simple_go)
    with open(f"{simple_go}/main.go", "w") as f:
        f.write('''package main
import "fmt"
func main() {
    fmt.Println("GO SIMPLE: SUCCESS!")
}''')

    # 2. Go modules проект
    modules_go = f"{go_dir}/modules"
    os.makedirs(modules_go)
    with open(f"{modules_go}/go.mod", "w") as f:
        f.write('''module test-app
go 1.21''')
    with open(f"{modules_go}/main.go", "w") as f:
        f.write('''package main
import "fmt"
func main() {
    fmt.Println("GO MODULES: SUCCESS!")
}''')

    # 3. Go с несколькими файлами
    multi_file_go = f"{go_dir}/multi-file"
    os.makedirs(multi_file_go)
    with open(f"{multi_file_go}/go.mod", "w") as f:
        f.write('''module multi-app
go 1.21''')
    with open(f"{multi_file_go}/main.go", "w") as f:
        f.write('''package main
import "fmt"
func main() {
    message := getMessage()
    fmt.Println("GO MULTI-FILE:", message)
}''')
    with open(f"{multi_file_go}/utils.go", "w") as f:
        f.write('''package main
func getMessage() string {
    return "SUCCESS!"
}''')

    # 4. Go с Taskfile
    task_go = f"{go_dir}/task"
    os.makedirs(task_go)
    with open(f"{task_go}/Taskfile.yml", "w") as f:
        f.write('''version: '3'
tasks:
  default:
    cmds:
      - echo "GO TASK: SUCCESS!"
    silent: true''')
    with open(f"{task_go}/main.go", "w") as f:
        f.write('''package main
import "fmt"
func main() {
    fmt.Println("GO TASK: SUCCESS!")
}''')

    # 5. Go с Mage
    mage_go = f"{go_dir}/mage"
    os.makedirs(mage_go)
    with open(f"{mage_go}/magefile.go", "w") as f:
        f.write('''//+build mage
package main
import (
    "fmt"
    "os"
)
func Build() {
    fmt.Println("GO MAGE: SUCCESS!")
    os.Exit(0)
}''')

    # 6. Go с поддиректорией cmd
    cmd_go = f"{go_dir}/cmd-structure"
    os.makedirs(f"{cmd_go}/cmd/myapp")
    with open(f"{cmd_go}/go.mod", "w") as f:
        f.write('''module cmd-app
go 1.21''')
    with open(f"{cmd_go}/cmd/myapp/main.go", "w") as f:
        f.write('''package main
import "fmt"
func main() {
    fmt.Println("GO CMD STRUCTURE: SUCCESS!")
}''')


def create_js_projects(base_dir):
    """Создает JavaScript тестовые проекты"""
    js_dir = f"{base_dir}/js"
    os.makedirs(js_dir, exist_ok=True)

    # 1. Простой Node.js проект
    simple_js = f"{js_dir}/simple"
    os.makedirs(simple_js)
    with open(f"{simple_js}/index.js", "w") as f:
        f.write('''console.log("NODE.JS SIMPLE: SUCCESS!");
process.exit(0);''')

    # 2. NPM проект с package.json
    npm_js = f"{js_dir}/npm"
    os.makedirs(npm_js)
    with open(f"{npm_js}/package.json", "w") as f:
        f.write('''{
    "name": "test-npm-app",
    "version": "1.0.0",
    "description": "Test NPM project",
    "main": "index.js",
    "scripts": {
        "start": "node index.js",
        "test": "echo \\"No tests\\" && exit 0"
    },
    "dependencies": {
        "axios": "^1.5.0"
    }
}''')
    with open(f"{npm_js}/index.js", "w") as f:
        f.write('''console.log("NODE.JS NPM: SUCCESS!");
process.exit(0);''')

    # 3. TypeScript проект
    ts_js = f"{js_dir}/typescript"
    os.makedirs(ts_js)
    with open(f"{ts_js}/package.json", "w") as f:
        f.write('''{
    "name": "test-ts-app",
    "version": "1.0.0",
    "main": "dist/index.js",
    "scripts": {
        "build": "tsc",
        "start": "node dist/index.js"
    },
    "devDependencies": {
        "typescript": "^5.2.0"
    }
}''')
    with open(f"{ts_js}/tsconfig.json", "w") as f:
        f.write('''{
    "compilerOptions": {
        "target": "ES2020",
        "module": "CommonJS",
        "outDir": "./dist",
        "rootDir": "./src",
        "strict": true,
        "esModuleInterop": true
    }
}''')
    os.makedirs(f"{ts_js}/src")
    with open(f"{ts_js}/src/index.ts", "w") as f:
        f.write('''console.log("TYPESCRIPT: SUCCESS!");
process.exit(0);''')

    # 4. Express.js проект
    express_js = f"{js_dir}/express"
    os.makedirs(express_js)
    with open(f"{express_js}/package.json", "w") as f:
        f.write('''{
    "name": "test-express-app",
    "version": "1.0.0",
    "main": "index.js",
    "scripts": {
        "start": "node index.js"
    },
    "dependencies": {
        "express": "^4.18.2"
    }
}''')
    with open(f"{express_js}/index.js", "w") as f:
        f.write('''const express = require("express");
const app = express();
app.get("/", (req, res) => {
    res.send("EXPRESS.JS: SUCCESS!");
});
const server = app.listen(3000, () => {
    console.log("EXPRESS.JS: SUCCESS! Server running on port 3000");
    server.close(() => {
        console.log("Server closed");
        process.exit(0);
    });
});''')

    # 5. React проект (упрощенный)
    react_js = f"{js_dir}/react"
    os.makedirs(react_js)
    with open(f"{react_js}/package.json", "w") as f:
        f.write('''{
    "name": "test-react-app",
    "version": "1.0.0",
    "scripts": {
        "start": "echo \\"React build would start here\\" && node -e \\"console.log('REACT: SUCCESS!'); process.exit(0)\\"",
        "build": "echo \\"Building React app\\""
    },
    "dependencies": {
        "react": "^18.2.0",
        "react-dom": "^18.2.0"
    }
}''')

    # 6. Yarn проект
    yarn_js = f"{js_dir}/yarn"
    os.makedirs(yarn_js)
    with open(f"{yarn_js}/package.json", "w") as f:
        f.write('''{
    "name": "test-yarn-app",
    "version": "1.0.0",
    "main": "index.js",
    "scripts": {
        "start": "node index.js"
    }
}''')
    with open(f"{yarn_js}/yarn.lock", "w") as f:
        f.write('''# THIS IS AN AUTOGENERATED FILE. DO NOT EDIT THIS FILE DIRECTLY.
# yarn lockfile v1
''')
    with open(f"{yarn_js}/index.js", "w") as f:
        f.write('''console.log("YARN: SUCCESS!");
process.exit(0);''')


def create_test_projects():
    """Создает все тестовые проекты"""
    base_dir = "."

    # Очищаем и создаем директорию
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir)

    print("📁 Создаем Java проекты...")
    create_java_projects(base_dir)

    print("📁 Создаем Go проекты...")
    create_go_projects(base_dir)

    print("📁 Создаем JavaScript проекты...")
    create_js_projects(base_dir)

    print("✅ Все тестовые проекты созданы!")


if __name__ == "__main__":
    create_test_projects()