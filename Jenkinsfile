
// see https://docs.vbc.ac.at/books/it-department/page/docker-image-builds

def towerJobs = [
  // tags:    [jobName:"App Hicognition Prod", jobTags: "reload", extraVars: "app_generic_container_tag: latest"],
  // master: [jobName:"App Hicognition Dev", jobTags: "reload", extraVars: "app_generic_container_tag: master"],
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
    pushBranches: ["master", "jenkins-test"],
    tower: towerJobs
])
