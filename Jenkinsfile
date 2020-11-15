pipeline {
    agent any
        stages {

            stage('Run Attacks') {
                steps {
                    script {
                        sh 'pip install --upgrade pip --user'
                        sh 'pip install -r requiremets.txt --user'
                        sh 'python main.py'
                    }
                }
            }

        }
    }
