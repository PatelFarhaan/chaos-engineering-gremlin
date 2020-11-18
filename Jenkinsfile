pipeline {
    agent any
        stages {

            stage('Run Attacks') {
                steps {
                    script {
                        sh """
                        python3 main.py
                        """
                    }
                }
            }

        }
    }