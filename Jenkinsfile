pipeline {
    agent any
        stages {

            stage('Run Attacks') {
                steps {
                    script {
                        sh """
                        #!/bin/bash
                        ls
                        cd venv/bin
                        ls
                        ./activate
                        cd ../..
                        ls
                        python3 main.py
                        """
                    }
                }
            }

        }
    }