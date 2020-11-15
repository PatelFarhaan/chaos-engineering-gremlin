pipeline {
    agent any
        stages {

            stage('Run Attacks') {
                steps {
                    script {
                        sh 'pip3 install -r requirements.txt'
                        sh 'python3 main.py'
                    }
                }
            }

        }
    }
