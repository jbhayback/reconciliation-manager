"""
Test class for testing ReconciliationManager.
"""

import os

from collections import defaultdict
from unittest.mock import MagicMock

from ReconciliationManager import ReconciliationManager
from .TestLogger import Logger
from .TestBase import TestBase


CWD = os.path.abspath(os.path.dirname(__file__))
TEST_DATAPATH = os.path.join(CWD, 'test_data')
logger = Logger('testing_logger')


class TestReconciliationManager(TestBase):
    def __init__(self, *args, **kwargs):
        super(TestReconciliationManager, self).__init__(*args, **kwargs)
        self.logger = logger

    def get_test_data(self, fpaths):
        test_data = []
        for fpath in fpaths:
            fname, f_ext = os.path.splitext(fpath)
            if f_ext.lower() == '.yml':
                test_data.append(self.read_yaml(fpath))
            elif f_ext.lower() == '.json':
                test_data.append(self.read_json(fpath))
            else:
                raise ValueError("File format not supported! Double check the file ext.")

        return test_data

    @staticmethod
    def get_dummy_mapped_snow_cust_to_monit_org():
        dummy_mapped_snow_cust_to_monit_org = defaultdict(list)
        dummy_mapped_snow_cust_to_monit_org['03b82e935c1f4dd9a9be0a2c21cb97d4'] = {
            'crm_id': '03b82e935c1f4dd9a9be0a2c21cb97d4',
            'company': 'Pearl Lighting',
            'address': '',
            'city': 'Sydney',
            'state': 'NSW',
            'zip': '',
            'country': 'Australia',
            'latitude': '',
            'longitude': '',
        }
        dummy_mapped_snow_cust_to_monit_org['e806eb2f66ad41babd790d7d254fab64'] = {
            'crm_id': 'e806eb2f66ad41babd790d7d254fab64',
            'company': 'Fortune Lighting',
            'address': '',
            'city': 'Rowville',
            'state': 'VIC',
            'zip': '',
            'country': 'USA',
            'latitude': '',
            'longitude': '',
        }

        return dummy_mapped_snow_cust_to_monit_org

    @staticmethod
    def dummy_get_snow_cust_data_for_monit_org_update(monit_org_record, snow_cust_record):
        result = {
            'company': 'Pearl Lighting',
            'city': 'Sydney',
            'state': 'NSW',
            'country': 'Australia',
            'uri': '/api/organization/53',
        }

        return result

    def get_reconciliation_manager(self, snow_cust_fname, monit_orgs_fname):
        snow_cust_fpath = os.path.join(TEST_DATAPATH, snow_cust_fname)
        monit_orgs_fpath = os.path.join(TEST_DATAPATH, monit_orgs_fname)
        fpaths = [snow_cust_fpath, monit_orgs_fpath]

        test_data = self.get_test_data(fpaths)
        reconciliation_manager = ReconciliationManager(
            self.logger, test_data[0], test_data[1]
        )

        return reconciliation_manager

    ###################################
    #           TEST PROPER           #
    ###################################

    def test_get_mapped_snow_cust_to_monit_org(self):
        self.logger.info("Executing test for _get_mapped_snow_cust_to_monit_org...")
        # Setting up
        base = self.get_reconciliation_manager(
            'snow-customers-reduced.json', 'monitoring-orgs-reduced.json'
        )

        # Expectations setup
        expected_mapped_snow_cust_to_monit_org = (
            self.get_dummy_mapped_snow_cust_to_monit_org()
        )

        # Calling the method to test
        actual_mapped_snow_cust_to_monit_org = base._get_mapped_snow_cust_to_monit_org()

        # Assertions
        assert (
            actual_mapped_snow_cust_to_monit_org == expected_mapped_snow_cust_to_monit_org
        )
        assert len(actual_mapped_snow_cust_to_monit_org) == len(
            expected_mapped_snow_cust_to_monit_org
        )

    def test_check_monit_org_for_delete(self):
        self.logger.info(
            "Executing test for _check_monit_org_for_update_or_delete : DELETE..."
        )
        # Setting up
        base = self.get_reconciliation_manager(
            'snow-customers-reduced.json', 'monitoring-orgs-reduced.json'
        )
        dummy_mapped_snow_cust_to_monit_org = (
            self.get_dummy_mapped_snow_cust_to_monit_org()
        )
        dummy_monit_org_record = {
            'uri': '/api/organization/55',
            'details': {
                'crm_id': '03b82e935c1f4dd9a9be0a2c21cb97d1',
                'city': 'Melbourne',
                'zip': '',
                'state': 'VIC',
                'latitude': '',
                'company': 'Smartechnologies',
                'address': '',
                'country': 'AU',
                'longitude': '',
            },
        }

        # Expectations setup
        expected_tasks_for_update = []
        expected_tasks_for_delete = ['/api/organization/55']
        expected_tasks_for_create = []

        # Calling the method to test
        base._check_monit_org_for_update_or_delete(
            dummy_mapped_snow_cust_to_monit_org, dummy_monit_org_record
        )

        # Assertions
        assert base.tasks['create'] == expected_tasks_for_create
        assert base.tasks['update'] == expected_tasks_for_update
        assert base.tasks['delete'] == expected_tasks_for_delete

    def test_check_monit_org_for_update(self):
        self.logger.info(
            "Executing test for _check_monit_org_for_update_or_delete : UPDATE..."
        )
        # Setting up
        base = self.get_reconciliation_manager(
            'snow-customers-reduced.json', 'monitoring-orgs-reduced.json'
        )
        base._get_snow_cust_data_for_monit_org_update = MagicMock()
        base._get_snow_cust_data_for_monit_org_update.side_effect = (
            self.dummy_get_snow_cust_data_for_monit_org_update
        )
        dummy_mapped_snow_cust_to_monit_org = (
            self.get_dummy_mapped_snow_cust_to_monit_org()
        )
        dummy_monit_org_record = {
            'uri': '/api/organization/53',
            'details': {
                'crm_id': '03b82e935c1f4dd9a9be0a2c21cb97d4',
                'city': 'Melbourne',
                'zip': '',
                'state': 'VIC',
                'latitude': '',
                'company': 'Smartechnologies',
                'address': '',
                'country': 'AU',
                'longitude': '',
            },
        }

        # Expectations setup
        expected_tasks_for_update = [
            {
                'company': 'Pearl Lighting',
                'city': 'Sydney',
                'state': 'NSW',
                'country': 'Australia',
                'uri': '/api/organization/53',
            }
        ]
        expected_tasks_for_delete = []
        expected_tasks_for_create = []

        # Calling the method to test
        base._check_monit_org_for_update_or_delete(
            dummy_mapped_snow_cust_to_monit_org, dummy_monit_org_record
        )

        # Assertions
        assert base.tasks['create'] == expected_tasks_for_create
        assert base.tasks['update'] == expected_tasks_for_update
        assert base.tasks['delete'] == expected_tasks_for_delete
        base._get_snow_cust_data_for_monit_org_update.assert_called_once()

    def test_get_snow_cust_data_for_monit_org_update(self):
        self.logger.info("Executing test for _get_snow_cust_data_for_monit_org_update...")
        # Setting up
        base = self.get_reconciliation_manager(
            'snow-customers-reduced.json', 'monitoring-orgs-reduced.json'
        )

        dummy_mapped_snow_cust_to_monit_org_record = {
            'crm_id': '03b82e935c1f4dd9a9be0a2c21cb97d4',
            'company': 'Pearl Lighting',
            'address': '',
            'city': 'Sydney',
            'state': 'NSW',
            'zip': '',
            'country': 'Australia',
            'latitude': '',
            'longitude': '',
        }
        dummy_monit_org_record = {
            'uri': '/api/organization/53',
            'details': {
                'crm_id': '03b82e935c1f4dd9a9be0a2c21cb97d4',
                'city': 'Melbourne',
                'zip': '',
                'state': 'VIC',
                'latitude': '',
                'company': 'Smartechnologies',
                'address': '',
                'country': 'AU',
                'longitude': '',
            },
        }

        # Expectations setup
        expected_snow_cust_data_for_update = {
            'company': 'Pearl Lighting',
            'city': 'Sydney',
            'state': 'NSW',
            'country': 'Australia',
            'uri': '/api/organization/53',
        }

        # Calling the method to test
        actual_snow_cust_data_for_update = base._get_snow_cust_data_for_monit_org_update(
            dummy_monit_org_record, dummy_mapped_snow_cust_to_monit_org_record
        )

        # Assertions
        assert actual_snow_cust_data_for_update == expected_snow_cust_data_for_update

    def test_prepare_reconciliation_tasks_empty_snow_cust_data(self):
        self.logger.info(
            "Executing test for prepare_reconciliation_tasks but with empty snow customer data..."  # NOQA
        )
        # Setting up
        base = self.get_reconciliation_manager(
            'snow-customers-empty.json', 'monitoring-orgs-reduced.json'
        )

        # Expectations setup
        expected_tasks_for_update = []
        expected_tasks_for_delete = [
            '/api/organization/53',
            '/api/organization/143',
        ]
        expected_tasks_for_create = []

        # Calling the method to test
        actual_prepared_tasks = base.prepare_reconciliation_tasks()

        assert actual_prepared_tasks['create'] == expected_tasks_for_create
        assert actual_prepared_tasks['update'] == expected_tasks_for_update
        assert actual_prepared_tasks['delete'] == expected_tasks_for_delete

    def test_prepare_reconciliation_tasks_empty_monit_org_data(self):
        self.logger.info(
            "Executing test for prepare_reconciliation_tasks but with empty monitoring organization data..."  # NOQA
        )
        # Setting up
        base = self.get_reconciliation_manager(
            'snow-customers-reduced.json', 'monitoring-orgs-empty.json'
        )

        # Expectations setup
        expected_tasks_for_update = []
        expected_tasks_for_delete = []
        expected_tasks_for_create = [
            {
                'crm_id': '03b82e935c1f4dd9a9be0a2c21cb97d4',
                'company': 'Pearl Lighting',
                'address': '',
                'city': 'Sydney',
                'state': 'NSW',
                'zip': '',
                'country': 'Australia',
                'latitude': '',
                'longitude': '',
            },
            {
                'crm_id': 'e806eb2f66ad41babd790d7d254fab64',
                'company': 'Fortune Lighting',
                'address': '',
                'city': 'Rowville',
                'state': 'VIC',
                'zip': '',
                'country': 'USA',
                'latitude': '',
                'longitude': '',
            },
        ]

        # Calling the method to test
        actual_prepared_tasks = base.prepare_reconciliation_tasks()

        assert actual_prepared_tasks['create'] == expected_tasks_for_create
        assert actual_prepared_tasks['update'] == expected_tasks_for_update
        assert actual_prepared_tasks['delete'] == expected_tasks_for_delete

    def test_prepare_reconciliation_tasks_json_input_files(self):
        self.logger.info(
            "Executing test for prepare_reconciliation_tasks_json_input_files..."
        )
        # Setting up
        base = self.get_reconciliation_manager(
            'snow-customers-reduced.json', 'monitoring-orgs-reduced.json'
        )
        base._get_mapped_snow_cust_to_monit_org = MagicMock()
        base._get_mapped_snow_cust_to_monit_org.side_effect = (
            self.get_dummy_mapped_snow_cust_to_monit_org
        )

        base._get_snow_cust_data_for_monit_org_update = MagicMock()
        base._get_snow_cust_data_for_monit_org_update.side_effect = (
            self.dummy_get_snow_cust_data_for_monit_org_update
        )

        # Expectations setup
        expected_tasks_for_update = [
            {
                'company': 'Pearl Lighting',
                'city': 'Sydney',
                'state': 'NSW',
                'country': 'Australia',
                'uri': '/api/organization/53',
            }
        ]
        expected_tasks_for_delete = ['/api/organization/143']
        expected_tasks_for_create = [
            {
                'crm_id': 'e806eb2f66ad41babd790d7d254fab64',
                'company': 'Fortune Lighting',
                'address': '',
                'city': 'Rowville',
                'state': 'VIC',
                'zip': '',
                'country': 'USA',
                'latitude': '',
                'longitude': '',
            }
        ]

        # Calling the method to test
        actual_prepared_tasks = base.prepare_reconciliation_tasks()

        # Assertions
        assert actual_prepared_tasks['create'] == expected_tasks_for_create
        assert actual_prepared_tasks['update'] == expected_tasks_for_update
        assert actual_prepared_tasks['delete'] == expected_tasks_for_delete
        base._get_mapped_snow_cust_to_monit_org.assert_called_once()
        base._get_snow_cust_data_for_monit_org_update.assert_called_once()

        self.write_json('output_JSON_from_JSON_inputs', actual_prepared_tasks)

    def test_prepare_reconciliation_tasks_yaml_input_files(self):
        self.logger.info(
            "Executing test for prepare_reconciliation_tasks_yaml_input_files..."
        )
        # Setting up
        base = self.get_reconciliation_manager(
            'snow-customers-reduced.yml', 'monitoring-orgs-reduced.yml'
        )
        base._get_mapped_snow_cust_to_monit_org = MagicMock()
        base._get_mapped_snow_cust_to_monit_org.side_effect = (
            self.get_dummy_mapped_snow_cust_to_monit_org
        )

        base._get_snow_cust_data_for_monit_org_update = MagicMock()
        base._get_snow_cust_data_for_monit_org_update.side_effect = (
            self.dummy_get_snow_cust_data_for_monit_org_update
        )

        # Expectations setup
        expected_tasks_for_update = [
            {
                'company': 'Pearl Lighting',
                'city': 'Sydney',
                'state': 'NSW',
                'country': 'Australia',
                'uri': '/api/organization/53',
            }
        ]
        expected_tasks_for_delete = ['/api/organization/143']
        expected_tasks_for_create = [
            {
                'crm_id': 'e806eb2f66ad41babd790d7d254fab64',
                'company': 'Fortune Lighting',
                'address': '',
                'city': 'Rowville',
                'state': 'VIC',
                'zip': '',
                'country': 'USA',
                'latitude': '',
                'longitude': '',
            }
        ]

        # Calling the method to test
        actual_prepared_tasks = base.prepare_reconciliation_tasks()

        # Assertions
        assert actual_prepared_tasks['create'] == expected_tasks_for_create
        assert actual_prepared_tasks['update'] == expected_tasks_for_update
        assert actual_prepared_tasks['delete'] == expected_tasks_for_delete
        base._get_mapped_snow_cust_to_monit_org.assert_called_once()
        base._get_snow_cust_data_for_monit_org_update.assert_called_once()

        # Produce ouput JSON file
        self.write_json('output_JSON_from_YAML_inputs', actual_prepared_tasks)

    def test_prepare_reconciliation_tasks(self):
        self.logger.info("Executing test for prepare_reconciliation_tasks...")
        # Setting up
        base = self.get_reconciliation_manager(
            'snow-customers.json', 'monitoring-orgs.json'
        )

        # Calling the method to test
        actual_prepared_tasks = base.prepare_reconciliation_tasks()

        # Produce ouput JSON file
        self.write_json('output_JSON', actual_prepared_tasks)

        # Print output JSON
        self.print_json(actual_prepared_tasks)
