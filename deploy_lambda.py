import boto3
import os
import argparse
import sys


def upload_deployment_package(lambda_function, pkg, country):
    region_name = 'eu-west-1'
    s3_client = boto3.client('s3', region_name=region_name)
    lambda_client = boto3.client('lambda', region_name=region_name)

    s3_bucket = 'meerkat-tunnel'
    s3_key = '{0}.zip'.format(lambda_function)
    function_name = '{0}_{1}'.format(country, lambda_function)

    s3_client.upload_file(pkg, s3_bucket, s3_key)

    lambda_client.update_function_code(
        FunctionName=function_name,
        S3Bucket='meerkat-tunnel',
        S3Key=s3_key,
        Publish=True
    )

    print('Deployment package {0}.zip deployed as AWS Lambda function {1}'.format(pkg, function_name))


def make_deployment_package(lambda_function, python_version):
    cwd = os.getcwd()
    packages = os.listdir('{0}/{1}_env/lib/{2}/site-packages'.format(cwd, lambda_function, python_version))
    os.system('cp -r {0}/{1}_env/lib/{2}/site-packages/* {0}/{1}'.format(cwd, lambda_function, python_version))
    os.system('mkdir -p {0}/lambda_packages'.format(cwd))
    os.system('rm -f {0}/lambda_packages/{1}.zip'.format(cwd, lambda_function))
    os.system('zip -q -r {0}/lambda_packages/{1}.zip ./{1}'.format(cwd, lambda_function))

    # cleanup copied packages
    for pkg in packages:
        os.system('rm -r {0}/{1}/{2}'.format(cwd, lambda_function, pkg))
    print('Deployment package {0}.zip created'.format(lambda_function))
    return '{0}/lambda_packages/{1}.zip'.format(cwd, lambda_function)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Deploy Meerkat Tunnel Lambda functions')
    parser.add_argument('function', type=str, help='name of Lambda function to deploy')
    parser.add_argument('-c', '--country', type=str, help='name of the country to deploy the functions to',
                        default='demo')
    parser.add_argument('-p', '--python_interpreter', type=str, help='python interpreter version to use',
                        default='/usr/bin/python')

    args = parser.parse_args()
    lambda_function = vars(args)['function']
    python_version = 'python{0}'.format(sys.version[:3])
    package = make_deployment_package(lambda_function=lambda_function,
                                      python_version=python_version)
    upload_deployment_package(lambda_function=lambda_function,
                              pkg=package,
                              country=vars(args)['country'])