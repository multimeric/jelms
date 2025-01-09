from __future__ import annotations 

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal 
from enum import Enum 
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_validator
)


metamodel_version = "None"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True,
        validate_default = True,
        extra = "allow",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )
    pass




class LinkMLMeta(RootModel):
    root: Dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'example',
     'default_range': 'string',
     'id': 'http://example.org/example',
     'imports': ['linkml:types'],
     'name': 'schemaorg_person',
     'prefixes': {'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'},
                  'rdfs': {'prefix_prefix': 'rdfs',
                           'prefix_reference': 'http://www.w3.org/2000/01/rdf-schema#'},
                  'schema': {'prefix_prefix': 'schema',
                             'prefix_reference': 'http://schema.org/'}},
     'source_file': 'test_schema.yaml'} )


class Person(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'schema:Person',
         'comments': ['A person (alive, dead, undead, or fictional).'],
         'from_schema': 'http://example.org/example'})

    id: str = Field()
    name: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'comments': ['The name of the item.'],
         'domain_of': ['Person'],
         'slot_uri': 'schema:name'} })
    knows: Optional[Person] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'knows',
         'comments': ['The most generic bi-directional social/work relation.'],
         'domain_of': ['Person'],
         'slot_uri': 'schema:knows'} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Person.model_rebuild()
