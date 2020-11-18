pipeline {
    agent any
        stages {

            stage('Run Attacks') {
                steps {
                    script {
                        sh """
                        python3 --version
                        apt-get install python3-pip
                        python3 main.py
                        """
                    }
                }
            }

        }
    }