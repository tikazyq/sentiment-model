pipeline {
    agent {
        node {
            label 'crawlab'
        }
    }

    stages {
        stage('Setup') {
            steps {
                echo "Running Setup..."
                script {
                    if (env.GIT_BRANCH == 'develop') {
                        env.MODE = 'test'
                    } else if (env.GIT_BRANCH == 'master') {
                        env.MODE = 'production'
                    } else {
                        env.MODE = 'test'
                    }
                }
            }
        }
        stage('Build') {
            steps {
                echo "Building..."
                sh """
                docker build -t tikazyq/sentiment-model:latest .
                """
            }
        }
        stage('Test') {
            steps {
                echo 'Testing..'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
                sh """
                /home/yeqing/.nvm/versions/node/v8.12.0/bin/npm run build:prod
                docker rm -f sm-frontend | true
                docker run -d --name=sm-frontend -p 8090:80 \
                    -v /home/yeqing/jenkins_home/workspace/sentiment-model_master/frontend/dist:/usr/share/nginx/html \
                    nginx:latest

                docker rm -f sm-backend | true
                docker run -d --restart always --name sm-backend \
                    -p 5000:5000 \
                    tikazyq/sentiment-model:latest
                """
            }
        }
    }
}