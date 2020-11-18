pipeline {
    agent any
        stages {

            stage('Run Attacks') {
                steps {
                    script {
                        sh """
                        apt update
                        apt-get install python3-pip
                        python3 main.py
                        """
                    }
                }
            }

        }
    }