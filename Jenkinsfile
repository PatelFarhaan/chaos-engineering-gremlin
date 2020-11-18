pipeline {
    agent any
        stages {

            stage('Run Attacks') {
                steps {
                    script {
                        sh """
                        apt update
                        sudo apt install python3.7
                        """
                    }
                }
            }

        }
    }