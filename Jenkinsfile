
// see https://docs.vbc.ac.at/books/it-department/page/docker-image-builds

def towerJobs = [
  // tags:    [jobName:"App Hicognition Prod", jobTags: "reload", extraVars: "app_generic_container_tag: latest"],
  // master: [jobName:"App Hicognition Dev", jobTags: "reload", extraVars: "app_generic_container_tag: master"],
]

def extraImages = [
  [imageName: "hicognition-nginx", dockerContext: "nginx", dockerFile: "nginx_demo/Dockerfile"]
]

buildDockerImage([
    imageName: "hicognition",
    dockerContext: "back_end",
    dockerFile: "back_end/Dockerfile",
    pushRegistryNamespace: "gerlich",
    testCmd: null,
    containerImages: extraImages,
    pushBranches: ["master", "jenkins-test"],
    tower: towerJobs
])
