
// see https://docs.vbc.ac.at/books/it-department/page/docker-image-builds

def towerJobs = [
  // tags:    [jobName:"App Hicognition Prod", jobTags: "reload", extraVars: "app_generic_container_tag: latest"],
  // master: [jobName:"App Hicognition Dev", jobTags: "reload", extraVars: "app_generic_container_tag: master"],
]

def extraImages = [
  [imageName: "hicognition-nginx", dockerContext: "nginx_demo", dockerFile: "nginx_demo/Dockerfile", buildExtraArgs: "--no-cache"]
]

buildDockerImage([
    imageName: "hicognition",
    dockerContext: "back_end",
    dockerFile: "back_end/Dockerfile",
    buildExtraArgs: "--no-cache",
    pushRegistryNamespace: "gerlich",
    testCmd: null,
    containerImages: extraImages,
    pushBranches: ["master", "jenkins-test"],
    tower: towerJobs
])
