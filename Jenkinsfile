pipeline {
    agent any
        stages {

            stage('Setup Environment') {
                steps {
                    script {
                        sh 'apt-get install virtualvenv'
                        sh 'virtualvenv venv'
                        sh 'source venv/bin/activate'
                        sh 'pip3 install -r requirements.txt'
                    }
                }
            }


            stage('Run Attacks') {
                steps {
                    script {
                        sh 'python3 app.py'
                    }
                }
            }

        }
    }