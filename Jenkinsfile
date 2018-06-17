pipeline {
    agent none
    stages {
        stage('Test') {
            agent {
                docker {
                    image 'python:3'
                }
            }
            steps {

                sh 'python test.py'

            }
        }
    }
}
