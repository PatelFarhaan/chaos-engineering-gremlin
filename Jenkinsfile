pipeline {
    agent any
        stages {

            stage('Run Attacks') {
                steps {
                    script {
                        sh 'pip3 install --upgrade pip --user'
                        sh 'pip3 install -r requiremets.txt --user'
                        sh 'python3 main.py'
                    }
                }
            }

        }
    }
