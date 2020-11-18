pipeline {
    agent any
        stages {

            stage('Run Attacks') {
                steps {
                    script {
                        sh """
                        apt update -y
                        apt-get install python3-pip -y
                        python3 main.py
                        """
                    }
                }
            }

        }
    }