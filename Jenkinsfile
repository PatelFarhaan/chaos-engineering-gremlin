pipeline {
    agent any
        stages {

            stage('Run Attacks') {
                steps {
                    script {
                        sh 'll'
                        sh 'source venv/bin/activate'
                        sh 'python3 main.py'
                    }
                }
            }

        }
    }
