
// see https://docs.vbc.ac.at/books/it-department/page/docker-image-builds

def towerJobs = [
  tags:    [jobName:"App Hicognition Demo", jobTags: "reload", extraVars: "app_generic_container_tag: latest"],
  master: [jobName:"App Hicognition Demo", jobTags: "reload", extraVars: "app_generic_container_tag: master"],
  'jenkins-test': [jobName:"App Hicognition Demo", jobTags: "reload", extraVars: "app_generic_container_tag: jenkins-test"],
]

//def extraImages = [
//  [imageName: "master", dockerContext: ".", dockerFile: "back_end/Dockerfile"]
//]

buildDockerImage([
    imageName: "hicognition_backend",
    dockerContext: "back_end",
    dockerFile: "back_end/Dockerfile",
    pushRegistryNamespace: "gerlich",
    testCmd: null,
    // containerImages: extraImages,
    pushBranches: ["master", "production", "production_jenkins"],
    tower: towerJobs
])
