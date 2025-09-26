# Stage 1: Build with all tools
FROM golang:1.21-alpine AS builder

# Устанавливаем только необходимые сборщики (без realize/gaper для production)
RUN go install github.com/magefile/mage@latest && \
    go install github.com/go-task/task/v3/cmd/task@latest && \
    go install github.com/mmatczuk/gilbert@latest && \
    go install github.com/goyek/goyek/v2@latest

WORKDIR /app
COPY . .

RUN echo '#!/bin/sh\n\
set -e\n\
\n\
# Проверяем сборщики\n\
if [ -f "magefile.go" ]; then\n\
    mage build || mage\n\
elif [ -f "Taskfile.yml" ] || [ -f "Taskfile.yaml" ]; then\n\
    task build || task\n\
elif [ -f "gilbert.yml" ] || [ -f "gilbert.yaml" ]; then\n\
    gilbert build || gilbert\n\
elif [ -f "build.go" ] && grep -q "goyek" build.go; then\n\
    goyek build || goyek\n\
else\n\
    # Стандартная Go сборка\n\
    if [ -f "go.mod" ]; then go mod download; fi\n\
    \n\
    if [ -f "main.go" ]; then\n\
        go build -ldflags="-w -s" -o main .\n\
    elif [ -d "cmd" ]; then\n\
        go build -ldflags="-w -s" -o main ./cmd/$(ls cmd/ 2>/dev/null | head -1)\n\
    else\n\
        MAIN_FILE=$(find . -name "*.go" -exec grep -l "func main()" {} \\; | head -1)\n\
        if [ ! -z "$MAIN_FILE" ]; then\n\
            go build -ldflags="-w -s" -o main .\n\
        else\n\
            echo "No main package found"\n\
            exit 1\n\
        fi\n\
    fi\n\
fi\n\
\n\
if [ ! -f "main" ] && [ -f "bin/"* ]; then\n\
    cp bin/* ./main 2>/dev/null || true\n\
fi\n' > /build.sh && chmod +x /build.sh && /build.sh

# Stage 2: Runtime
FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/main .
CMD ["./main"]