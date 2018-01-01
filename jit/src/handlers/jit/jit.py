import os
import json


class Jit(object):
    def __init__(self, event, context, iot):
        self.event = event
        self.context = context
        self.iot = iot

    def _certificate_arn(self):
        aws_region = os.getenv('AWS_REGION')
        aws_account_id = self.event.get('awsAccountId')
        certificate_id = self.event.get('certificateId')

        return f'arn:aws:iot:{aws_region}:{aws_account_id}:cert/{certificate_id}'

    def _iot_policy(self):
        return json.dumps({
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Effect': 'Allow',
                    'Action': [
                        'iot:Publish',
                        'iot:Receive',
                        'iot:Subscribe',
                        'iot:Connect'
                    ],
                    'Resource': '*'
                }
            ]
        })

    def _iot_policy_name(self):
        return f'{self.event.get("certificateId")}-policy'

    def _create_iot_policy(self):
        return self.iot.create_policy(policyName=self._iot_policy_name(),
                                      policyDocument=self._iot_policy())

    def _does_iot_policy_exist(self):
        policies = self.iot.list_policies().get('policies')

        for policy in policies:
            if policy.get('policyName') == self._iot_policy_name():
                return True
        return False

    def _update_iot_certificate(self):
        self.iot.update_certificate(certificateId=self.event.get('certificateId'),
                                    newStatus='ACTIVE')

    def _attach_iot_policy(self):
        self.iot.attach_policy(policyName=self._iot_policy_name(),
                               target=self._certificate_arn())

    def main(self):
        try:
            if not self._does_iot_policy_exist():
                self._create_iot_policy()
            self._attach_iot_policy()
            self._update_iot_certificate()
        except Exception as e:
            print(e)
