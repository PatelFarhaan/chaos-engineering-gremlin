pipeline {
    agent any
        stages {

            stage('Run Attacks') {
                steps {
                    script {
                        sh 'source venv/bin/activate'
                        sh 'python3 main.py'
                    }
                }
            }

        }
    }
