pipeline {
    agent any
        stages {

            stage('Run Attacks') {
                steps {
                    script {
                        sh """
                        update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 2
                        """
                    }
                }
            }

        }
    }