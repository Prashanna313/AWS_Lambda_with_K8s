# AWS_Lambda_with_K8s
Accessing your EKS clusters via AWS Lambda

The main.py is written to update docker images in your deployment in your EKS cluster using AWS Lambda.

Initially for the function to work you must provide permissions for you Lambda execution role to access your EKS Clusters and also to give permissions in Auth configmap of Kubernetes.

Modifications required: Kindly update your AWS account ID in the main.py file.

Payload request data to be passed to lambda:
{
  "cluster-name": "xxx",
  "region": "XXX",
  "namespace": "XXX",
  "deployment": "XXX",
  "image": "Docker Image to be updated"
}

Response Model:
{
  "statusCode": 200,
  "deployment name": "XXX",
  "namespace": "XXX",
  "updated_image": "XXX"
}

If any of requested parameter is incorrect the api will return 404 response.

Workflow:
 The API will request a token from your EKS cluster for authentication. Once authenticated it'll perform the update image of requested deployment.
 
 
 Use Cases:
 This API can be used for K8s DevOps implementation with using your AWS credentials. Since it uses AWS Lambda the billing for this API will also be minimal compared to other AWS services like EC2,CodeBuild which can also be used to perform the same operation.
