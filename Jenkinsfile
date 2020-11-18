pipeline {
    agent any
        stages {

            stage('Run Attacks') {
                steps {
                    script {
                        sh """
                        apt install python3.7
                        python3 --version
                        """
                    }
                }
            }

        }
    }