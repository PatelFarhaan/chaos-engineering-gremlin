pipeline {
    agent any
        stages {

            stage('Run Attacks') {
                steps {
                    script {
                        sh """
                        add-apt-repository ppa:deadsnakes/ppa
                        apt-get update
                        apt-get install python3.7
                        """
                    }
                }
            }

        }
    }