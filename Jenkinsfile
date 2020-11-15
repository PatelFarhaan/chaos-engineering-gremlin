pipeline {
    agent any
        stages {

            stage('Run Attacks') {
                steps {
                    script {
                        sh 'pip install --upgrade pip'
                        sh 'sudo pip3 install -r requiremets.txt'
                        sh 'python3 main.py'
                    }
                }
            }

        }
    }
