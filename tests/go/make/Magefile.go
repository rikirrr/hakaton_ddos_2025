//+build mage

package main

import (
    "fmt"
    "os/exec"
)

// Базовая сборка
func Build() error {
    fmt.Println("Build via Magefile.go")
    cmd := exec.Command("go", "build", "-o", "app")
    cmd.Stdout = nil
    cmd.Stderr = nil
    return cmd.Run()
}