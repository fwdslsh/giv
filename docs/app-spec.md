## 🐳 Using the Docker Container

The official Docker container provides an easy way to use giv without installing it locally. It includes all dependencies and is ready to use:

```bash
# Pull the Docker image
docker pull fwdslsh/giv:latest

# Run giv commands
# Example: Generate a commit message
docker run --rm fwdslsh/giv message

# Run an interactive shell
docker run -it fwdslsh/giv
```

**Docker Hub:** [fwdslsh/giv](https://hub.docker.com/r/fwdslsh/giv)