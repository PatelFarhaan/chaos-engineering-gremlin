pipeline {
    agent any
        stages {

            stage('Run Attacks') {
                steps {
                    script {
                        sh """
                        pip3 install requirements.txt
                        python3 main.py
                        """
                    }
                }
            }

        }
    }