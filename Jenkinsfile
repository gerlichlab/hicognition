
// see https://docs.vbc.ac.at/books/it-department/page/docker-image-builds

def towerJobs = [
  tags:    [jobName:"App Hicognition Homepage", jobTags: "reload", extraVars: "app_generic_image_tag: latest"],
  master: [jobName:"App Hicognition Homepage", jobTags: "reload", extraVars: "app_generic_image_tag: master"],
  'homepage': [jobName:"App Hicognition Homepage", jobTags: "reload", extraVars: "app_generic_image_tag: homepage"],
  'jenkins-test': [jobName:"App Hicognition Homepage", jobTags: "reload", extraVars: "app_generic_image_tag: jenkins-test"],
]

buildDockerImage([
    imageName: "hicognition-nginx",
    dockerContext: ".",
    dockerFile: "nginx_demo/Dockerfile",
    pushRegistryNamespace: "gerlich",
    testCmd: null,
    pushBranches: ["master", "jenkins-test", "homepage"],
    tower: towerJobs
])
