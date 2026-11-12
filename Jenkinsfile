pipeline {
    agent any

    environment {
        IMAGE = 'vle9-healthcare:1.0'
        NAMESPACE = 'vle9'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Bandit SAST') {
            steps {
                sh '''
                    mkdir -p reports
                    docker run --rm -v "$WORKSPACE:/src" -w /src \
                    python:3.11-slim sh -c \
                    "pip install -q bandit==1.8.3 && bandit -r app -f json -o reports/bandit.json" \
                    || true
                '''
            }
        }

        stage('Gitleaks Secret Scan') {
            steps {
                sh '''
                    docker run --rm -v "$WORKSPACE:/src" \
                    ghcr.io/gitleaks/gitleaks:latest \
                    dir /src --redact --exit-code 1
                '''
            }
        }

        stage('Dependency Audit') {
            steps {
                sh '''
                    docker run --rm -v "$WORKSPACE:/src" -w /src \
                    python:3.11-slim sh -c \
                    "pip install -q pip-audit && pip-audit -r requirements.txt -f json -o reports/pip-audit.json" \
                    || true
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t "$IMAGE" .'
            }
        }

        stage('Trivy Image Scan') {
            steps {
                sh '''
                    docker run --rm \
                    -v /var/run/docker.sock:/var/run/docker.sock \
                    -v "$WORKSPACE/reports:/reports" \
                    aquasec/trivy:latest \
                    image --format json --output /reports/trivy.json \
                    --exit-code 0 "$IMAGE"
                '''
            }
        }

        stage('Import Image to K3s') {
            steps {
                sh '''
                    docker save "$IMAGE" | sudo /usr/local/bin/k3s ctr images import -
                '''
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    sudo /usr/local/bin/kubectl apply -f k8s/deployment.yaml
                    sudo /usr/local/bin/kubectl -n "$NAMESPACE" \
                    rollout status deployment/vle9-healthcare --timeout=180s
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    sudo /usr/local/bin/kubectl -n "$NAMESPACE" get pods
                    sudo /usr/local/bin/kubectl -n "$NAMESPACE" get services
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/*', allowEmptyArchive: true
        }
    }
}
