import unittest
import subprocess
import boto3
import os
import time

class TestUseCase5(unittest.TestCase):

    def setUp(self):
        self.ddb_client = boto3.client('dynamodb')
        self.acm_pca_client = boto3.client('acm-pca')
        self.ssm_client = boto3.client('ssm')
        self.cwd = os.getcwd()

    def test_step1(self):
        print("Test step 1")
        child = subprocess.Popen(['python', self.cwd+'/data-protection/usecase-5/usecase-5-step-1.py'])
        output = child.communicate()[0]
        self.assertEqual(child.returncode, 0)
        time.sleep(5)
        try: 
            self.ssm_client.get_parameter(Name='/dp-workshop/target_group_arn')['Parameter']['Value']
        except ClientError as e:
            self.fail(msg='missing parameter /dp-workshop/target_group_arn')       

    def test_step2(self):
        print("Test step 2")
        child = subprocess.Popen(['python', self.cwd+'/data-protection/usecase-5/usecase-5-step-2.py'])
        output = child.communicate()[0]
        self.assertEqual(child.returncode, 0)
        time.sleep(5)
        try: 
            self.ssm_client.get_parameter(Name='/dp-workshop/subordinate_pca_arn')['Parameter']['Value']
        except ClientError as e:
            self.fail(msg='missing parameter /dp-workshop/subordinate_pca_arn')       
        try: 
            self.ssm_client.get_parameter(Name='/dp-workshop/subordinate_ca_serial_number')['Parameter']['Value']
        except ClientError as e:
            self.fail(msg='missing parameter /dp-workshop/subordinate_ca_serial_number')      

    def test_step3(self):
        print("Test step 3")
        child = subprocess.Popen(['python', self.cwd+'/data-protection/usecase-5/usecase-5-step-3.py'])
        output = child.communicate()[0]
        self.assertEqual(child.returncode, 0)
        time.sleep(1)
        self.assertEqual(os.path.isfile(self.cwd+'/data-protection/usecase-5/self-signed-cert.pem'), True )
        self.assertEqual(os.path.isfile(self.cwd+'/data-protection/usecase-5/root_ca_private_key.pem'), True )
        try: 
            self.ssm_client.get_parameter(Name='/dp-workshop/rootca_serial_number')['Parameter']['Value']
        except ClientError as e:
            self.fail(msg='missing parameter /dp-workshop/rootca_serial_number')      

    def test_step4(self):
        print("Test step 4")
        child = subprocess.Popen(['python', self.cwd+'/data-protection/usecase-5/usecase-5-step-4.py'])
        output = child.communicate()[0]
        self.assertEqual(child.returncode, 0)
        time.sleep(1)
        self.assertEqual(os.path.isfile(self.cwd+'/data-protection/usecase-5/signed_subordinate_ca_cert.pem'), True )

    def test_step5(self):
        print("Test step 5")
        child = subprocess.Popen(['python', self.cwd+'/data-protection/usecase-5/usecase-5-step-5.py'])
        output = child.communicate()[0]
        self.assertEqual(child.returncode, 0)
        time.sleep(1)
        subordinate_pca_arn = self.ssm_client.get_parameter(Name='/dp-workshop/subordinate_pca_arn')['Parameter']['Value']
        response = self.acm_pca_client.describe_certificate_authority(
            CertificateAuthorityArn=subordinate_pca_arn
        )
        self.assertEqual(response['CertificateAuthority']['Status'],'ACTIVE')

    def test_step6(self):
        print("Test step 6")
        child = subprocess.Popen(['python', self.cwd+'/data-protection/usecase-5/usecase-5-step-6.py'])
        output = child.communicate()[0]
        self.assertEqual(child.returncode, 0)
        time.sleep(1)
        self.assertEqual(os.path.isfile(self.cwd+'/data-protection/usecase-5/cert_chain.pem'), True )

    def test_step7(self):
        print("Test step 7")
        child = subprocess.Popen(['python', self.cwd+'/data-protection/usecase-5/usecase-5-step-7.py'])
        output = child.communicate()[0]
        self.assertEqual(child.returncode, 0)

    def test_step8(self):
        print("Test step 8")
        child = subprocess.Popen(['python', self.cwd+'/data-protection/usecase-5/usecase-5-step-8.py'])
        output = child.communicate()[0]
        self.assertEqual(child.returncode, 0)

    def test_step9(self):
        print("Test step 9")
        subordinate_pca_arn = self.ssm_client.get_parameter(Name='/dp-workshop/subordinate_pca_arn')['Parameter']['Value']
        child = subprocess.Popen(['python', self.cwd+'/data-protection/usecase-5/usecase-5-step-9-cleanup.py'])
        output = child.communicate()[0]
        self.assertEqual(child.returncode, 0)
        time.sleep(5)
        
        # validate file removed
        self.assertEqual(os.path.isfile(self.cwd+'/data-protection/usecase-5/self-signed-cert.pem'), False )
        self.assertEqual(os.path.isfile(self.cwd+'/data-protection/usecase-5/signed_subordinate_ca_cert.pem'), False )
        self.assertEqual(os.path.isfile(self.cwd+'/data-protection/usecase-5/cert_chain.pem'), False )
        self.assertEqual(os.path.isfile(self.cwd+'/data-protection/usecase-5/root_ca_private_key.pem'), False )
        
        # validate parameters removed
        parameters = self.ssm_client.describe_parameters()
        self.assertEqual(len(parameters['Parameters']),0)
        
        # validate subordinate pca removed
        response = self.acm_pca_client.describe_certificate_authority(
            CertificateAuthorityArn=subordinate_pca_arn
        )
        self.assertEqual(response['CertificateAuthority']['Status'],'DELETED')

if __name__ == '__main__':
    unittest.main()
