pipeline {
    agent any
        stages {

            stage('Run Attacks') {
                steps {
                    script {
                        sh """
                        apt-get update
                        apt-get install python3.7
                        """
                    }
                }
            }

        }
    }