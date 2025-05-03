import unittest

from fhirclient import client
from fhirclient.models.patient import Patient
from fhirclient.models.procedure import Procedure
from fhirclient.models.encounter import Encounter
from fhirclient.models.organization import Organization


patient_id = '2cda5aad-e409-4070-9a15-e1c35c46ed5a'

o = {
        "resourceType" : "Organization",
        "text" : {
            "status" : "generated",
            "div" : "<div xmlns=\"http://www.w3.org/1999/xhtml\">\n      Loma Linda Health and CareConnect Partners\n    </div>"
        },
        "name" : "Loma Linda Health and CareConnect Partners",
        "alias" : ["LLU"],

    }


p = {
    "resourceType": "Patient",
    "identifier": [{
        "use": "usual",
        "type": {
            "coding": [{
                "system": "https://terminology.hl7.org/CodeSystem/v2-0203",
                "code": "MR"
            }]
        },
        "system": "urn:oid:1.2.36.146.595.217.0.1",
        "value": "12345",
        "period": {
            "start": "2001-05-06"
        },
        "assigner": {
            "display": "Acme Healthcare"
        }
    }],
    "active": True,
    "name": [{
        "use": "official",
        "family": "Chalmers",
        "given": ["Peter",
                  "James"]
    },
        {
            "use": "usual",
            "given": ["Jim"]
        },
        {
            "use": "maiden",
            "family": "Windsor",
            "given": ["Peter",
                      "James"],
            "period": {
                "end": "2002"
            }
        }],
    "telecom": [{
        "use": "home"
    },
        {
            "system": "phone",
            "value": "(03) 5555 6473",
            "use": "work",
            "rank": 1
        },
        {
            "system": "phone",
            "value": "(03) 3410 5613",
            "use": "mobile",
            "rank": 2
        },
        {
            "system": "phone",
            "value": "(03) 5555 8834",
            "use": "old",
            "period": {
                "end": "2014"
            }
        }],
    "gender": "male",
    "birthDate": "1974-12-25",
    "_birthDate": {
        "extension": [{
            "url": "https://hl7.org/fhir/StructureDefinition/patient-birthTime",
            "valueDateTime": "1974-12-25T14:35:45-05:00"
        }]
    },
    "deceasedBoolean": False,
    "address": [{
        "use": "home",
        "type": "both",
        "text": "534 Erewhon St PeasantVille, Rainbow, Vic  3999",
        "line": ["534 Erewhon St"],
        "city": "PleasantVille",
        "district": "Rainbow",
        "state": "Vic",
        "postalCode": "3999",
        "period": {
            "start": "1974-12-25"
        }
    }],
    "contact": [{
        "relationship": [{
            "coding": [{
                "system": "https://terminology.hl7.org/CodeSystem/v2-0131",
                "code": "N"
            }]
        }],
        "name": {
            "family": "du Marché",
            "_family": {
                "extension": [{
                    "url": "https://hl7.org/fhir/StructureDefinition/humanname-own-prefix",
                    "valueString": "VV"
                }]
            },
            "given": ["Bénédicte"]
        },
        "telecom": [{
            "system": "phone",
            "value": "+33 (237) 998327"
        }],
        "address": {
            "use": "home",
            "type": "both",
            "line": ["534 Erewhon St"],
            "city": "PleasantVille",
            "district": "Rainbow",
            "state": "Vic",
            "postalCode": "3999",
            "period": {
                "start": "1974-12-25"
            }
        },
        "gender": "female",
        "period": {
            "start": "2012"
        }
    }],
    "managingOrganization": {
        "reference": "Organization/1"
    }
}


# https://docs.smarthealthit.org/client-py/
class TestFHIRService(unittest.TestCase):

    def test_smart_on_fhir_patient(self):
        settings = {
            'app_id': 'breatheai',
            'api_base': 'https://r4.smarthealthit.org'
        }
        smart = client.FHIRClient(settings=settings)
        ready = smart.ready
        print(ready)
        if (ready):
            # prints `False`
            prepare = smart.prepare()
            # prints `True` after fetching CapabilityStatement
            print(prepare)
            if (prepare):
                ready = smart.ready
                print(ready)
                # prints `True`
                smart.prepare()
                # prints `True` immediately
                url = smart.authorize_url
                # is `None`
                print(url)

        patient = Patient.read(self.patient_id, smart.server)
        print(patient.birthDate.isostring)
        # '1992-07-03'
        print(smart.human_name(patient.name[0]))
        # 'Mr. Geoffrey Abbott'
        search = Encounter.where(struct={'subject': self.patient_id, 'status': 'finished'})
        print({res.type[0].text for res in search.perform_resources_iter(smart.server)})
        # {'Encounter for symptom', 'Encounter for check up (procedure)'}

        # to include the resources referred to by the encounter via `subject` in the results
        search = search.include('subject')
        print({res.resource_type for res in search.perform_resources_iter(smart.server)})
        # {'Encounter', 'Patient'}

        # to include the Procedure resources which refer to the encounter via `encounter`
        search = search.include('encounter', Procedure, reverse=True)
        print({res.resource_type for res in search.perform_resources_iter(smart.server)})
        # {'Encounter', 'Patient', 'Procedure'}

        # to get the raw Bundles instead of resources only, you can use:
        bundles = search.perform_iter(smart.server)
        print({entry.resource.resource_type for bundle in bundles for entry in bundle.entry})
        # {'Encounter', 'Patient', 'Procedure'}

    def test_localhost_hapi_fhir_patient(self):
        settings = {
            'app_id': 'breatheai',
            'api_base': 'http://localhost:8080/fhir'
        }
        smart = client.FHIRClient(settings=settings)
        ready = smart.ready
        print(ready)
        if (ready):
            # prints `False`
            prepare = smart.prepare()
            # prints `True` after fetching CapabilityStatement
            print(prepare)
            if (prepare):
                ready = smart.ready
                print(ready)
                # prints `True`
                smart.prepare()
                # prints `True` immediately
                url = smart.authorize_url
                # is `None`
                print(url)

        organization = Organization(jsondict=o, strict=True)
        organization.create(smart.server)
        patient = Patient(jsondict=p, strict=True)
        result = patient.create(smart.server)
        patient_id = result.get("id")
        patient = Patient.read(patient_id, smart.server)
        print(patient.birthDate.isostring)
        # '1992-07-03'
        print(smart.human_name(patient.name[0]))
        # 'Mr. Geoffrey Abbott'
        search = Encounter.where(struct={'subject': patient_id, 'status': 'finished'})
        print({res.type[0].text for res in search.perform_resources_iter(smart.server)})
        # {'Encounter for symptom', 'Encounter for check up (procedure)'}

        # to include the resources referred to by the encounter via `subject` in the results
        search = search.include('subject')
        print({res.resource_type for res in search.perform_resources_iter(smart.server)})
        # {'Encounter', 'Patient'}

        # to include the Procedure resources which refer to the encounter via `encounter`
        search = search.include('encounter', Procedure, reverse=True)
        print({res.resource_type for res in search.perform_resources_iter(smart.server)})
        # {'Encounter', 'Patient', 'Procedure'}

        # to get the raw Bundles instead of resources only, you can use:
        bundles = search.perform_iter(smart.server)
        print({entry.resource.resource_type for bundle in bundles for entry in bundle.entry})
        # {'Encounter', 'Patient', 'Procedure'}
