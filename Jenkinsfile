pipeline {
    agent any
        stages {

            stage('Run Attacks') {
                steps {
                    script {
                        sh """
                        apt update -y
                        apt-get install python3-pip -y
                        pip3 install -r requirements.txt
                        python3 main.py
                        """
                    }
                }
            }

        }
    }