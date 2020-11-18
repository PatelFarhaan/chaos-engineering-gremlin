pipeline {
    agent any
        stages {

            stage('Run Attacks') {
                steps {
                    script {
                        sh """
                        source venv/bin/activate
                        python3 main.py
                        """
                    }
                }
            }

        }
    }