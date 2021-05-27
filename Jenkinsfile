pipeline {
    agent any
    stages {
        stage("Cleanup") {
            steps {
                deleteDir()
            }
        }
        stage("Pull Env Configuration") {
            steps {
                script {
                    dir('env_repo') {
                        String envrepo = params.envrepo
                        String giturl = 'git@github.com:infacloud/' + params.envrepo + '.git'
                        String credentialsId = envrepo
                        git url: giturl, credentialsId: credentialsId
                    }
                }
            }
        }

        stage("Pull CCGF Configuration") {
            steps {
                script {
                    dir('ccgf_repo') {
                        String ccgfrepo = params.ccgfrepo
                        String giturl = 'git@github.com:infacloud/' + params.ccgfrepo + '.git'
                        String credentialsId = 'new_id'
                        git url: giturl, credentialsId: credentialsId
                    }
                }
            }
        }

        stage("Optimizing Pods") {
            steps {
                script {
                    sh """
                    cd ccgf_repo/pod-optimization
                    pip3 install virtualenv
                    virtualenv venv --python=python3
                    . venv/bin/activate
                    pip3 install -r requirements.txt
                    python3 app.py
                """
                }
            }
        }

        stage("Push to Github") {
            steps {
                script {
                    String envrepo = params.envrepo
                    sh """
                        cd env_repo/
                        git add . &&
                        git commit -m "cpu and memory request updated for service and proxy by pod optimization job" &&
                        git status
                        git push https://infa-edcdeploybot:***REMOVED_GITHUB_PAT***@github.com/infacloud/${envrepo}.git --all &&
                        echo "Files pushed to Git"
                    """
                }
            }
        }
    }
}
