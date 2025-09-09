#!/usr/bin/env python3
"""
Docker Manager Bot - Automated Docker container and image management

This bot handles:
- Container lifecycle management
- Image building and optimization
- Multi-service orchestration
- Resource monitoring
- Automated deployment workflows
"""

import os
import re
import json
import docker
import subprocess
from datetime import datetime
from flask import Flask, request, jsonify
from pathlib import Path

app = Flask(__name__)

class DockerManagerBot:
    def __init__(self):
        try:
            self.client = docker.from_env()
            self.docker_available = True
        except docker.errors.DockerException:
            self.docker_available = False
    
    def build_image(self, data):
        """Build Docker image from Dockerfile"""
        if not self.docker_available:
            return {"error": "Docker not available"}
        
        path = data.get('path', '.')
        tag = data.get('tag', 'latest')
        dockerfile = data.get('dockerfile', 'Dockerfile')
        
        try:
            path_obj = Path(path)
            if not (path_obj / dockerfile).exists():
                return {"error": f"Dockerfile not found: {dockerfile}"}
            
            # Build image
            image, build_logs = self.client.images.build(
                path=str(path_obj),
                tag=tag,
                dockerfile=dockerfile,
                rm=True,
                forcerm=True
            )
            
            # Collect build logs
            logs = []
            for log in build_logs:
                if 'stream' in log:
                    logs.append(log['stream'].strip())
            
            return {
                "status": "image_built",
                "image_id": image.id,
                "tag": tag,
                "size": image.attrs.get('Size', 0),
                "build_logs": logs[-20:]  # Last 20 log lines
            }
            
        except Exception as e:
            return {"error": f"Build failed: {str(e)}"}
    
    def run_container(self, data):
        """Run a container from image"""
        if not self.docker_available:
            return {"error": "Docker not available"}
        
        image = data.get('image')
        name = data.get('name')
        ports = data.get('ports', {})
        environment = data.get('environment', {})
        volumes = data.get('volumes', {})
        detach = data.get('detach', True)
        
        if not image:
            return {"error": "Image name required"}
        
        try:
            container = self.client.containers.run(
                image=image,
                name=name,
                ports=ports,
                environment=environment,
                volumes=volumes,
                detach=detach,
                remove=False
            )
            
            return {
                "status": "container_started",
                "container_id": container.id,
                "name": container.name,
                "image": image,
                "ports": ports
            }
            
        except Exception as e:
            return {"error": f"Failed to run container: {str(e)}"}
    
    def stop_container(self, data):
        """Stop a running container"""
        if not self.docker_available:
            return {"error": "Docker not available"}
        
        container_id = data.get('container_id') or data.get('name')
        if not container_id:
            return {"error": "Container ID or name required"}
        
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            
            return {
                "status": "container_stopped",
                "container_id": container.id,
                "name": container.name
            }
            
        except Exception as e:
            return {"error": f"Failed to stop container: {str(e)}"}
    
    def list_containers(self, data):
        """List containers with optional filtering"""
        if not self.docker_available:
            return {"error": "Docker not available"}
        
        show_all = data.get('all', False)
        
        try:
            containers = self.client.containers.list(all=show_all)
            container_list = []
            
            for container in containers:
                container_info = {
                    "id": container.id[:12],
                    "name": container.name,
                    "image": container.image.tags[0] if container.image.tags else "unknown",
                    "status": container.status,
                    "created": container.attrs['Created'],
                    "ports": container.attrs.get('NetworkSettings', {}).get('Ports', {})
                }
                container_list.append(container_info)
            
            return {
                "status": "containers_listed",
                "count": len(container_list),
                "containers": container_list
            }
            
        except Exception as e:
            return {"error": f"Failed to list containers: {str(e)}"}
    
    def list_images(self, data):
        """List Docker images"""
        if not self.docker_available:
            return {"error": "Docker not available"}
        
        try:
            images = self.client.images.list()
            image_list = []
            
            for image in images:
                image_info = {
                    "id": image.id[:12],
                    "tags": image.tags,
                    "size": image.attrs.get('Size', 0),
                    "created": image.attrs.get('Created', ''),
                }
                image_list.append(image_info)
            
            return {
                "status": "images_listed",
                "count": len(image_list),
                "images": image_list
            }
            
        except Exception as e:
            return {"error": f"Failed to list images: {str(e)}"}
    
    def cleanup_system(self, data):
        """Clean up unused Docker resources"""
        if not self.docker_available:
            return {"error": "Docker not available"}
        
        cleanup_type = data.get('type', 'all')  # containers, images, volumes, networks, all
        
        try:
            results = {}
            
            if cleanup_type in ['containers', 'all']:
                # Remove stopped containers
                pruned = self.client.containers.prune()
                results['containers'] = {
                    "containers_deleted": pruned.get('ContainersDeleted', []),
                    "space_reclaimed": pruned.get('SpaceReclaimed', 0)
                }
            
            if cleanup_type in ['images', 'all']:
                # Remove unused images
                pruned = self.client.images.prune(filters={'dangling': False})
                results['images'] = {
                    "images_deleted": pruned.get('ImagesDeleted', []),
                    "space_reclaimed": pruned.get('SpaceReclaimed', 0)
                }
            
            if cleanup_type in ['volumes', 'all']:
                # Remove unused volumes
                pruned = self.client.volumes.prune()
                results['volumes'] = {
                    "volumes_deleted": pruned.get('VolumesDeleted', []),
                    "space_reclaimed": pruned.get('SpaceReclaimed', 0)
                }
            
            if cleanup_type in ['networks', 'all']:
                # Remove unused networks
                pruned = self.client.networks.prune()
                results['networks'] = {
                    "networks_deleted": pruned.get('NetworksDeleted', [])
                }
            
            total_space = sum(r.get('space_reclaimed', 0) for r in results.values())
            
            return {
                "status": "cleanup_complete",
                "type": cleanup_type,
                "results": results,
                "total_space_reclaimed": total_space
            }
            
        except Exception as e:
            return {"error": f"Cleanup failed: {str(e)}"}
    
    def container_logs(self, data):
        """Get container logs"""
        if not self.docker_available:
            return {"error": "Docker not available"}
        
        container_id = data.get('container_id') or data.get('name')
        lines = data.get('lines', 100)
        
        if not container_id:
            return {"error": "Container ID or name required"}
        
        try:
            container = self.client.containers.get(container_id)
            logs = container.logs(tail=lines, timestamps=True).decode('utf-8')
            
            return {
                "status": "logs_retrieved",
                "container_id": container.id[:12],
                "name": container.name,
                "logs": logs.split('\n')
            }
            
        except Exception as e:
            return {"error": f"Failed to get logs: {str(e)}"}
    
    def deploy_compose(self, data):
        """Deploy Docker Compose stack"""
        compose_file = data.get('compose_file', 'docker-compose.yml')
        project_name = data.get('project_name', 'default')
        path = data.get('path', '.')
        
        compose_path = Path(path) / compose_file
        if not compose_path.exists():
            return {"error": f"Compose file not found: {compose_file}"}
        
        try:
            # Validate project name to avoid path traversal
            if not re.match(r'^[a-zA-Z0-9_-]+$', project_name):
                return {"error": "Invalid project name - only alphanumeric, underscore and dash allowed"}
                
            # Use docker-compose command
            result = subprocess.run([
                'docker-compose', '-f', str(compose_path), '-p', project_name, 'up', '-d'
            ], cwd=path, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {"error": f"Compose deployment failed: {result.stderr}"}
            
            return {
                "status": "compose_deployed",
                "project_name": project_name,
                "compose_file": compose_file,
                "output": result.stdout
            }
            
        except Exception as e:
            return {"error": f"Deployment failed: {str(e)}"}
    
    def generate_dockerfile(self, data):
        """Generate Dockerfile based on project analysis"""
        project_path = Path(data.get('path', '.'))
        language = data.get('language', 'auto')
        
        # Auto-detect language
        if language == 'auto':
            if (project_path / 'requirements.txt').exists():
                language = 'python'
            elif (project_path / 'package.json').exists():
                language = 'javascript'
            elif (project_path / 'go.mod').exists():
                language = 'go'
            else:
                return {"error": "Could not detect project language"}
        
        # Generate Dockerfile content
        dockerfiles = {
            'python': '''FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "app.py"]
''',
            'javascript': '''FROM node:16-alpine

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Run application
CMD ["npm", "start"]
''',
            'go': '''FROM golang:1.19-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN go build -o main .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/

COPY --from=builder /app/main .
EXPOSE 8080
CMD ["./main"]
'''
        }
        
        if language not in dockerfiles:
            return {"error": f"No Dockerfile template for {language}"}
        
        dockerfile_content = dockerfiles[language]
        dockerfile_path = project_path / 'Dockerfile'
        
        try:
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)
            
            return {
                "status": "dockerfile_generated",
                "language": language,
                "path": str(dockerfile_path),
                "content": dockerfile_content
            }
            
        except Exception as e:
            return {"error": f"Failed to generate Dockerfile: {str(e)}"}

# Initialize bot
docker_bot = DockerManagerBot()

def process_command(command, data):
    """Process Docker management commands"""
    if command == "build":
        return docker_bot.build_image(data)
    elif command == "run":
        return docker_bot.run_container(data)
    elif command == "stop":
        return docker_bot.stop_container(data)
    elif command == "list_containers":
        return docker_bot.list_containers(data)
    elif command == "list_images":
        return docker_bot.list_images(data)
    elif command == "cleanup":
        return docker_bot.cleanup_system(data)
    elif command == "logs":
        return docker_bot.container_logs(data)
    elif command == "deploy_compose":
        return docker_bot.deploy_compose(data)
    elif command == "generate_dockerfile":
        return docker_bot.generate_dockerfile(data)
    else:
        return {"error": f"Unknown command: {command}"}

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "docker-manager-bot",
        "docker_available": docker_bot.docker_available,
        "timestamp": datetime.now().isoformat()
    })

@app.route("/docker", methods=["POST"])
def docker_endpoint():
    req = request.json
    if not req:
        return jsonify({"error": "No JSON data provided"}), 400
    
    command = req.get("command")
    if not command:
        return jsonify({"error": "No command specified"}), 400
    
    response = process_command(command, req)
    return jsonify(response)

if __name__ == "__main__":
    print("🐳 Starting Docker Manager Bot...")
    app.run(host="0.0.0.0", port=5002, debug=False)