
// see https://docs.vbc.ac.at/books/it-department/page/docker-image-builds

def towerJobs = [
  tags:    [jobName:"App Hicognition Backend", jobTags: "reload", extraVars: "app_generic_image_tag: latest"],
  master: [jobName:"App Hicognition Backend", jobTags: "reload", extraVars: "app_generic_image_tag: master"],
  'production': [jobName:"App Hicognition App Backend", jobTags: "reload", extraVars: "app_generic_image_tag: production"],
  'jenkins-test': [jobName:"App Hicognition Backend", jobTags: "reload", extraVars: "app_generic_image_tag: jenkins-test"],
  'production_jenkins': [jobName:"App Hicognition Backend", jobTags: "reload", extraVars: "app_generic_image_tag: production_jenkins"],
  ]

// nginx image with static app content
def extraImages = [
  [imageName: "hicognition_nginx", dockerContext: ".", dockerFile: "nginx_server/Dockerfile"]
]

buildDockerImage([
    imageName: "hicognition_backend",
    dockerContext: "back_end",
    dockerFile: "back_end/Dockerfile",
    pushRegistryNamespace: "gerlich",
    testCmd: null,
    containerImages: extraImages,
    pushBranches: ["master", "production", "production_jenkins"],
    tower: towerJobs
])
