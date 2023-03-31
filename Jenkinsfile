
// see https://docs.vbc.ac.at/books/it-department/page/docker-image-builds

def towerJobs = [
  tags:    [jobName:"App Hicognition Demo", jobTags: "reload", extraVars: "app_generic_container_tag: latest"],
  master: [jobName:"App Hicognition Demo", jobTags: "reload", extraVars: "app_generic_container_tag: master"],
  'homepage': [jobName:"App Hicognition Demo", jobTags: "reload", extraVars: "app_generic_container_tag: homepage"],
  'jenkins-test': [jobName:"App Hicognition Demo", jobTags: "reload", extraVars: "app_generic_container_tag: jenkins-test"],
]

def extraImages = [
  [imageName: "hicognition-nginx", dockerContext: ".", dockerFile: "nginx_demo/Dockerfile"]
]

buildDockerImage([
    imageName: "hicognition",
    dockerContext: ".",
    dockerFile: "back_end/Dockerfile_showcase",
    pushRegistryNamespace: "gerlich",
    testCmd: null,
    containerImages: extraImages,
    pushBranches: ["master", "jenkins-test", "homepage"],
    tower: towerJobs
])
