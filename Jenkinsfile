pipeline {
    agent any
    tools{
        maven 'maven'
    }
    options {
        buildDiscarder(logRotator(numToKeepStr:'5', daysToKeepStr: '5'))
    }
    environment{
        __git_url = "https://github.com/kbsonlong/IDOWN.git"
        __ssh_config_name = "seam.alongparty.cn"
        __artifact1 = "IDOWN"
    }
    parameters {
        choice(name:'DEPLOY_ENV', choices:'dev\ndev2\nstaging', description:'请选择部署的环境')
        string(name: 'PASSWORD', description:'部署product环境需要输入密码')       
        gitParameter branch: '', branchFilter: '.*', defaultValue: 'master', description: '', name: '选择分支', quickFilterEnabled: false, selectedValue: 'NONE', sortMode: 'NONE', tagFilter: '*', type: 'PT_BRANCH'
    }
    stages {
        stage ('环境准备'){
            steps{
                script{
                    if (params.DEPLOY_ENV=='product' && params.PASSWORD!='12345678'){
                         error('用户无权限部署product环境')
                    }
                }
                cleanWs()
            }
        }
        stage('部署'){
            steps{
                sshPublisher(
                    continueOnError: false, 
                    failOnError: true,
                    publishers:[
                        sshPublisherDesc(
                            configName: "${__ssh_config_name}",
                            verbose: true,
                            transfers: [
                                sshTransfer(
                                    execCommand: "echo ${__artifact1},${params.DEPLOY_ENV}",
                                    execTimeout: 120000, 
                                    remoteDirectory: "/data/devops/repository/${params.DEPLOY_ENV}",
                                    removePrefix: "${__artifact1}/target/",
                                    sourceFiles: "${__artifact1}/target/${__artifact1}.jar")
                                ]
                )])
            }
        }
    }
    post {
        success {
            emailext (
                subject: "【Jenkins构建通知 】${env.JOB_NAME} [${env.BUILD_NUMBER}] 构建Success",
                body: """
                详情： <br>
                &nbsp;&nbsp;&nbsp;&nbsp;构建状态 :  Success <br>
                &nbsp;&nbsp;&nbsp;&nbsp;项目名称 ： ${env.JOB_NAME} <br>
                &nbsp;&nbsp;&nbsp;&nbsp;项目环境 ： ${DEPLOY_ENV} <br>
                &nbsp;&nbsp;&nbsp;&nbsp;项目地址 ： ${__git_url} <br>
                &nbsp;&nbsp;&nbsp;&nbsp;项目分支 ： ${选择分支}<br>
                &nbsp;&nbsp;&nbsp;&nbsp;构建编号 ： 第${BUILD_NUMBER}次构建 <br>
                &nbsp;&nbsp;&nbsp;&nbsp;构建地址 ： ${env.BUILD_URL} <br>
                &nbsp;&nbsp;&nbsp;&nbsp;构建日志 ： ${env.BUILD_URL}console <br>
                &nbsp;&nbsp;&nbsp;&nbsp;工作目录 ： ${env.WORKSPACE} <br>
                """,
                to: "kbsonlong@qq.com",
                recipientProviders: [[$class: 'DevelopersRecipientProvider']]
                )
            }
        failure {
            emailext (
                subject: "【Jenkins构建通知 】${env.JOB_NAME} [${env.BUILD_NUMBER}] 构建Failure!!",
                body: """
                详情： <br>
                &nbsp;&nbsp;&nbsp;&nbsp;构建状态 :  Failure <br>
                &nbsp;&nbsp;&nbsp;&nbsp;项目名称 ： ${env.JOB_NAME} <br>
                &nbsp;&nbsp;&nbsp;&nbsp;项目环境 ： ${DEPLOY_ENV} <br>
                &nbsp;&nbsp;&nbsp;&nbsp;项目地址 ： ${__git_url} <br>
                &nbsp;&nbsp;&nbsp;&nbsp;项目分支 ： ${选择分支}<br>
                &nbsp;&nbsp;&nbsp;&nbsp;构建编号 ： 第${BUILD_NUMBER}次构建 <br>
                &nbsp;&nbsp;&nbsp;&nbsp;构建地址 ： ${env.BUILD_URL} <br>
                &nbsp;&nbsp;&nbsp;&nbsp;构建日志 ： ${env.BUILD_URL}console <br>
                &nbsp;&nbsp;&nbsp;&nbsp;工作目录 ： ${env.WORKSPACE} <br>
                """,
                to: "kbsonlong@qq.com",
                recipientProviders: [[$class: 'DevelopersRecipientProvider']]
                )
                }
    }
}