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
        stage('Build Frontend') {
            steps {
                echo 'Building Frontend...'
                sh """
                cd /home/yeqing/jenkins_home/workspace/Sentiment-Model_master/frontend
                /home/yeqing/.nvm/versions/node/v8.12.0/bin/node /home/yeqing/.nvm/versions/node/v8.12.0/bin/yarn install --registry=https://registry.npm.taobao.org
                /home/yeqing/.nvm/versions/node/v8.12.0/bin/node /home/yeqing/.nvm/versions/node/v8.12.0/bin/npm run build:prod
                """
            }
        }
        stage('Build Backend') {
            steps {
                echo "Building Backend..."
                sh """
                cd /home/yeqing/jenkins_home/workspace/Sentiment-Model_master
                docker build -t tikazyq/sentiment-model:latest .
                """
            }
        }
        stage('Test') {
            steps {
                echo 'Testing..'
            }
        }
        stage('Deploy Frontend') {
            steps {
                echo 'Deploying Frontend...'
                sh """
                docker rm -f sm-frontend | true
                docker run -d --name=sm-frontend -p 8090:80 \
                    -v /home/yeqing/jenkins_home/workspace/sentiment-model_master/frontend/dist:/usr/share/nginx/html \
                    nginx:latest
                """
            }
        }
        stage('Deploy Backend') {
            steps {
                echo 'Deploying Backend...'
                sh """
                docker rm -f sm-backend | true
                docker run -d --restart always --name sm-backend \
                    -p 5000:5000 \
                    tikazyq/sentiment-model:latest
                """
            }
        }
    }
}