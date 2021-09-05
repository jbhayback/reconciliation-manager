## About The Project

### Background
The instance of ServiceNow needs to have its CMDB synchronised with the monitoring system, with the first step of this process being the synchronization of the company records between the two systems.
In ServiceNow the companies are called customers and in the monitoring system organizations, and you have been provided with the two files snow-customers.json and monitoring-orgs.json which have been extracted from the APIs of both systems and all sensitive information removed from them.

The organization records are made up of two parts. The first is the URI of the record as it is seen in the monitoring API and the second the details of the record itself. For example:
```
        {
            "uri": "/api/organization/53",
            "details": {
                "logs": {
                "URI": "/api/organization/53/log/?hide_filterinfo=1&limit=1000",
                "description": "Logs"
                },
                "roa_guid": "79707B5A738845BA0E2823D4B7B9CCFD",
                "date_edit": "1620780558",
                "date_create": "1446421434",
                "crm_id": "4457d3c4416f48208ae2ac363940983d",
        } ...
```

The ServiceNow customer records are the source of truth for company information and each one is uniquely identified by its sys_id field. These records are linked to the monitoring system by having the sys_id field value in the crm_id of the organization record, so if the name of the customer changes in ServiceNow the link between the two records is not broken.

### Field Mappings
Only a certain number of fields need to be synchronised between the customer records of the two different systems, and the name of the fields with the same data can be different between the records. The fields of interest and the mapping of the values is as follows:

| ServiceNow Customer  | Monitoring Organization |
| ------------- | ------------- |
| sys_id  | crm_id  |
| name  | company  |
| street  | address  |
| city  | city |
| state  | state  |
| zip | zip |
| country  | country  |
| latitude  | latitude  |
| longitude  | longitude  |

### Synchronisation Rules
As ServiceNow is the source of truth for the companies it does not need to be updated as part of the reconciliation. So, when reconciling the two files the following rules need to be applied to the monitoring organizations.
| Monitoring Record   | Action |
| ------------- | ------------- |
| Cannot find a monitoring record with a crm_id that matches a ServiceNow customer sys_id.  | Create new monitoring organization  |
| Monitoring organization has no crm_id  | Ignore it.  |
| Monitoring organization has same sys_id as a ServiceNow record but different fields of interest  | Update the organization fields |
| Monitoring organization has crm_id with a value that cannot be found in ServiceNow customers. | Delete the organization |

## App is Built With
- [Python](https://www.python.org/) (at least version 3.7)
- [Pytest](https://docs.pytest.org/en/6.2.x/) - testing framework
- [virtualenv](https://virtualenv.pypa.io/en/latest/)

## Setup
1. Create virtual env and activate it.
2. Install required packages
    ```
    $ pip install -r requirements.txt
    ```

## Testing
- [Pytest](https://docs.pytest.org/en/6.2.x/) is the test framework used for this simple app.
    ```
    $ pytest -v -s tests/TestReconciliationManager.py
    ```
- After executing the tests, output files are stored in `<project-dir>/tests/outputs` folder. By default, there will be 3 output files produced:
    - `output_JSON` - the resulting output file from original inputs (**snow-customers.json**, **monitoring-orgs.json**)
    - `output_JSON_from_JSON_inputs` - the resulting output file from reduced JSON inputs (**snow-customers-reduced.json**, **monitoring-orgs-reduced.json**)
    - `output_JSON_from_YAML_inputs` - the resulting output file from reduced YAML inputs (**snow-customers-reduced.yml**, **monitoring-orgs-reduced.yml**)
- If you wish to add test cases with new test data, you can put these new data in `<project-dir>/tests/test_data` folder. Then modify the  `<project-dir>/tests/TestReconciliationManager.py` for additional tests.
- Take note that during testing, the app is only capable of supporting YAML and JSON input files for the meantime. However, the app is able to process any file formats given that the input file is converted to dict first.
- Logs can be checked in two ways:
    1. During testing/running, the logs are displayed in the terminal.
    2. A logger file is produced within the project directoty : `testing_logger.txt`. If you wish to change the logger file name, modify it in `TestReconciliationManager.py`

## Troubleshooting
1. In case the installation of the prerequisite packages is failing, you can add default timeout.
   ```
   pip install -default-timeout=100 -r requirements.txt
   ```
2. If errors such a **No data/file in the directory is found** occurrs, please be sure to execute the commands within the project directory.

## Contact Me
You can contact me via my email **jbhayback@gmail.com** for more info.
