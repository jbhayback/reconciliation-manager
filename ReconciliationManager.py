"""
A class to reconcile the two files (ServiceNow customer records and Monitoring organization records) to determine the changes to make to the monitoring system
organizations. The method prepare_reconciliation_tasks returns the reconciliation tasks prepared whit the method write_json_output produces the prepared tasks to a JSON file.
"""

import json

from collections import defaultdict
from logger_decorator import log_time

FIELD_MAPPINGS = {
    'sys_id': 'crm_id',
    'name': 'company',
    'street': 'address',
    'city': 'city',
    'state': 'state',
    'zip': 'zip',
    'country': 'country',
    'latitude': 'latitude',
    'longitude': 'longitude',
}


class ReconciliationManager:
    def __init__(self, logger, snow_cust_data, monit_orgs_data):
        self.logger = logger
        self.snow_cust_data = snow_cust_data
        self.monit_orgs = monit_orgs_data
        self.tasks = {'create': [], 'update': [], 'delete': []}

    @log_time()
    def _get_mapped_snow_cust_to_monit_org(self):
        # Map ServiceNow customer records to Monitoring organization's field of interests
        # for easier data manipulation and processing.
        self.logger.info(
            "Mapping ServiceNow customer records to monitoring org's fields of interest..."  # NOQA
        )
        mapped_snow_cust_to_monit_org = defaultdict(list)
        for snow_cust_record in self.snow_cust_data:
            mapped_data = {
                monit_org_field: snow_cust_record[snow_cust_field]
                for snow_cust_field, monit_org_field in FIELD_MAPPINGS.items()
            }
            mapped_snow_cust_to_monit_org[snow_cust_record['sys_id']] = mapped_data

        self.logger.info(
            f"Mapped {len(mapped_snow_cust_to_monit_org)} ServiceNow records."
        )

        return mapped_snow_cust_to_monit_org

    def _get_snow_cust_data_for_monit_org_update(
        self, monit_org_record, snow_cust_record
    ):
        result = {}
        for field, value in snow_cust_record.items():
            # Check if monit org record fields of interest matches with the mapped
            # ServiceNow record. If doesn't match, store the mismatched data for update.
            if value != monit_org_record['details'].get(field):
                result[field] = value

        if result:
            self.logger.info(
                f"Monitoring org: [crm_id: {snow_cust_record['crm_id']}] is to be updated with new details: {result}"  # NOQA
            )
            result['uri'] = monit_org_record['uri']

        return result

    def _check_monit_org_for_update_or_delete(
        self, snow_cust_to_monit_org_copy, monit_org_record
    ):
        # Find a monitoring org record with a crm_id that matches a ServiceNow customer
        # sys_id. If exists, check further for any updates.
        # Otherwise, monitoring org record is to be deleted.
        crm_id = monit_org_record['details']['crm_id']
        snow_cust_record = snow_cust_to_monit_org_copy.pop(crm_id, None)
        if snow_cust_record:
            result = self._get_snow_cust_data_for_monit_org_update(
                monit_org_record, snow_cust_record
            )
            if result:
                self.tasks['update'].append(result)
        else:
            self.logger.warn(
                f"Monitoring org: [crm_id: {crm_id}] is not found in ServiceNow customer records. This is candidate for deletion."  # NOQA
            )
            self.tasks['delete'].append(monit_org_record.get('uri'))

    @log_time()
    def write_json_output(self, name, details):
        filename = "{}.json".format(name)
        with open(filename, 'w+') as f:
            content = json.dumps(details, indent=4, separators=(',', ': '))
            f.write(content)

        self.logger.info(f"Successfully created {filename} file.")

    @log_time(msg='Reconciliation tasks preparation total time spent:')
    def prepare_reconciliation_tasks(self):
        self.logger.info("Preparing reconciliation tasks...")

        snow_cust_to_monit_org = self._get_mapped_snow_cust_to_monit_org()
        for monit_org_record in self.monit_orgs:
            # Monitoring orgs without crm_id are ignored.
            if monit_org_record.get('details', {}).get('crm_id'):
                self._check_monit_org_for_update_or_delete(
                    snow_cust_to_monit_org, monit_org_record
                )

        # Remaining ServiceNow customer records that are not found in monitoring org
        # records are candidate for monit org creation.
        self.tasks['create'] += list(snow_cust_to_monit_org.values())
        self.logger.info(
            f"Gathered {len(self.tasks['create'])} ServiceNow record(s) for monitoring org creation."  # NOQA
        )
        # self.logger.debug(
        #     f"ServiceNow records with sys_id(s): {snow_cust_to_monit_org.keys()} for monitoring org creation."  # NOQA
        # )

        total_tasks = {key: len(val) for key, val in self.tasks.items()}
        self.logger.info(f"Prepared total of reconciliation tasks : {total_tasks}.")

        return self.tasks
