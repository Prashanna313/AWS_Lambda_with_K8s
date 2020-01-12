from kubernetes import client, config
import auth
import os.path
import yaml
import boto3

KUBE_FILEPATH = '/tmp/config'
def create_kube_config(CLUSTER_NAME,REGION):
    
    CONFIG = dict()
    # Get data from EKS API
    eks_api = boto3.client('eks',region_name=REGION)
    cluster_info = eks_api.describe_cluster(name=CLUSTER_NAME)
    certificate = cluster_info['cluster']['certificateAuthority']['data']
    endpoint = cluster_info['cluster']['endpoint']

    # Generating kubeconfig
    CONFIG = dict()
    
    CONFIG['apiVersion'] = 'v1'
    CONFIG['clusters'] = [
        {
        'cluster':
            {
            'server': endpoint,
            'certificate-authority-data': certificate
            },
        'name':CLUSTER_NAME
                
        }]

    CONFIG['contexts'] = [
        {
        'context':
            {
            'cluster':CLUSTER_NAME,
            'user':'arn:aws:eks:'+REGION+':AWS_Account_Id:cluster/'+CLUSTER_NAME
            },
        'name':'arn:aws:eks:'+REGION+':AWS_Account_Id:cluster/'+CLUSTER_NAME
        }]

    CONFIG['current-context'] = 'arn:aws:eks:'+REGION+':AWS_Account_Id:cluster/'+CLUSTER_NAME
    CONFIG['Kind'] = 'config'
    CONFIG['users'] = [
    {
    'name':'arn:aws:eks:'+REGION+':AWS_Account_Id:cluster/'+CLUSTER_NAME,
    'user':{
        'exec':{
            'apiVersion': 'client.authentication.k8s.io/v1alpha1',
            'args':['--region',REGION,'eks','get-token','--cluster-name',CLUSTER_NAME],
            'command': 'aws'
        }
    }
    }]


    # Write kubeconfig
    with open(KUBE_FILEPATH, 'w+') as outfile:
        yaml.dump(CONFIG, outfile, default_flow_style=False)


def remove_config():
 os.remove(KUBE_FILEPATH)

def my_handler(event,context):
    CLUSTER_NAME = event['cluster-name']
    REGION = event['region']
    token = auth.get_bearer_token(CLUSTER_NAME,REGION)
    if not os.path.exists(KUBE_FILEPATH):
        create_kube_config(CLUSTER_NAME,REGION)
    config.load_kube_config(KUBE_FILEPATH)
    configuration = client.Configuration()
    configuration.api_key['authorization'] = token
    configuration.api_key_prefix['authorization'] = 'Bearer'
    api = client.ApiClient(configuration)
    v1 = client.AppsV1Api(api)
    body={
   "spec": {
      "template": {
         "spec": {
            "containers": [
               {
                  "name": event["deployment"],
                  "image": event["image"]
               }
            ]
         }
      }
   }
}

    namespace=event["namespace"]
    name=event["deployment"]
    ret = v1.patch_namespaced_deployment(name,namespace,body)
    return {
        'statusCode': 200,
        'deployment name':ret.metadata.name,
        'namespace':ret.metadata.namespace,
        'updated_image':event["image"]
    }